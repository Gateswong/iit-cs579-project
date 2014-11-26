print(__name__)
print(__package__)

from collector.twitter_wrapper import get_twitter, robust_request
from collector.timing import Timing
from collector.models import Tweet, get_connection
from collector import _info, _error, _debug, _warn
from collector import config

from argparse import ArgumentParser
import re
import simplejson
from pymongo import MongoClient

## Parse Command Line Arguments

ap = ArgumentParser()
ap.add_argument('keyword', type=str,
                help='The keyword to be searched.')
ap.add_argument('--config', type=str, default='Config',
                help='The object name of configure object in config.py')
args = ap.parse_args()

conf = getattr(config, args.config)
twitter = get_twitter(conf)
keyword = args.keyword

print(config)

db = get_connection(conf)

timing = Timing(60 * 15)

## Find the max_id from the searching history

max_id = None
with MongoClient(host=conf.MONGODB_IP, port=conf.MONGODB_PORT) as db_lowlevel:
    _db = db_lowlevel['cs579proj']
    _coll = _db['tweets']
    if _coll.find({'keyword':keyword}).count() > 0:
        _info('Finding the earliest record for keyword: %s' % keyword)
        _r = _coll.aggregate([
            { '$match': {'keyword':keyword} },
            { '$group': {'_id':'$item', 'max_id':{'$min':'$tweet.id'}}}
        ])
        if _r['ok'] == 1.0:
            max_id = int(_r['result'][0]['max_id'])
            _info('The earliest record has id of %d' % max_id)

## prepare to search

next_url_pattern = re.compile('max_id=(\d+)')
params = {
    'q':keyword,
    'count':100,
    'result_type':'recent',
    'include_entities':1,
}
while True:
    # bulid params
    if max_id is not None:
        params['max_id'] = max_id
    
    # search tweets
    _info('Searching tweets. max_id=%d' % (max_id if max_id is not None else -1))
    res = robust_request(twitter, 'search/tweets', params, timing)
    res = simplejson.loads(res.text)
    
    # Save tweets into database
    _info('Got %d tweets' % len(res['statuses']))
    for x in res['statuses']:
        tweet = db.Tweet()
        tweet['keyword'] = keyword
        tweet['tweet'] = x
        
        tweet.save()
        
    # Get next_url for next search
    try:
        next_url = res['search_metadata']['next_results']
        max_id = int(next_url_pattern.findall(next_url)[0])
    except KeyError as err:
        break
    
