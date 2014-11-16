import ConfigParser
import sys
import time
import simplejson
import re
import datetime
from logging import (info as _info,
                     error as _error,
                     warning as _warn,
                     debug as _debug,
                     getLogger,
                     INFO,
                     StreamHandler,
                     Formatter)

from TwitterAPI import TwitterAPI

import pymongo

root = getLogger()
root.setLevel(INFO)
ch = StreamHandler(sys.stdout)
ch.setLevel(INFO)
formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
root.addHandler(ch)

def get_twitter(config_file):
    """ Read the config_file and construct an instance of TwitterAPI.
    Args:
      config_file ... A config file in ConfigParser format with Twitter credentials
    Returns:
      An instance of TwitterAPI.
    """
    config = ConfigParser.ConfigParser()
    config.read(config_file)
    twitter = TwitterAPI(
                   config.get('twitter', 'consumer_key'),
                   config.get('twitter', 'consumer_secret'),
                   config.get('twitter', 'access_token'),
                   config.get('twitter', 'access_token_secret'))
    return twitter

twitter = get_twitter('default.cfg')
_info('Established Twitter connection.')

class Object(object):
    pass

timer = Object()
timer.interval = 60.0 * 15
timer.start = -1.0

searching = Object()
searching.since_id = 0
searching.max_id = 0

conf = Object()
conf.database_ip = '127.0.0.1'

def mongo_init(ip):
    client = pymongo.MongoClient(host=ip)
    db = client.cs579proj
    return db

def robust_request(twitter, resource, params, max_tries=5):
    """ If a Twitter request fails, sleep for 15 minutes.
    Do this at most max_tries times before quitting.
    Args:
      twitter .... A TwitterAPI object.
      resource ... A resource string to request.
      params ..... A parameter dictionary for the request.
      max_tries .. The maximum number of tries to attempt.
    Returns:
      A TwitterResponse object, or None if failed.
    """
    if timer.start == -1:
        timer.start = time.time()
    while True:
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            _info('robust_request did not return 200, sleeping...')
            time.sleep(timer.start - time.time() + timer.interval + 5)
            timer.start = time.time()
    return None

next_url_pattern = re.compile('max_id=(\d+)')
def search_tweets(keyword, max_id=None):
    params = {
        'q':keyword,
        'count':100,
        'include_entities':1,
        'result_type':'recent'
    }

    if max_id is None:
        cursor = conf.table_history.find({'keyword':keyword})
        if cursor.count() > 0:
            max_id = cursor[0]['max_id']
        
        
    _info('searching tweets... max_id={}'.format(max_id if max_id is not None else None))        
    
    if max_id is not None:
        params['max_id'] = max_id
    
    res = robust_request(
        twitter,
        'search/tweets',
        params
    )
    res_json = simplejson.loads(res.text)
    
    #max_id = res_json['search_metadata']['max_id']
    
    tweets = []
    for x in res_json['statuses']:
        dtstr = x['created_at']
        dt = datetime.datetime.strptime(dtstr, '%a %b %d %X +0000 %Y')
        if dt - datetime.datetime.now() > datetime.timedelta(1):
            conf.table_history.update(
                { 'keyword':keyword },
                {
                    '$set':{
                        'time':datetime.datetime.now(), 
                        'max_id':x['id']
                    }
                },
                upsert=True
            )
            return None, tweets
        tweets.append({
            'keyword':keyword,
            'id':x['id'],
            'created_at':x['created_at'],
            'text':x['text'],
            'user':x['user']['screen_name'],
            'name':x['user']['name']
        })
    
    try:
        next_url = res_json['search_metadata']['next_results']
        max_id = int(next_url_pattern.findall(next_url)[0])
        conf.table_history.update(
            { 'keyword':keyword },
            {
                '$set':{
                    'time':datetime.datetime.now(), 
                    'max_id':max_id
                }
            },
            upsert=True
        )        
    except KeyError as err:
        _info('no next search page, terminating...')
        return None, tweets
    
    return max_id, tweets



def fetch_tweets(keyword):
    _info('starting getting tweets for keyword {}'.format(keyword))

    max_id = None
    while True:
        max_id, tweets = search_tweets(keyword, max_id)
        _info('get {} tweets, next max_id={}'.format(len(tweets), max_id))
        
        for t in tweets:
            conf.table_tweets.insert(t)
        
        _info('saved {} tweets into database.'.format(len(tweets)))
        if max_id == None:
            break

if __name__ == '__main__':
    import sys
    if len(sys.argv) < 3:
        print('Usage: python dataman.py KEYWORD DATABASE_IP')
        exit(1)
    conf.database_ip = sys.argv[2]
    conf.database_tables = mongo_init(conf.database_ip)
    conf.table_tweets = conf.database_tables.tweets
    conf.table_history = conf.database_tables.history
    conf.max_id = None
    fetch_tweets(sys.argv[1])
    