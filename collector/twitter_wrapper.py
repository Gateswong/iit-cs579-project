from TwitterAPI import TwitterAPI
import re

import config

def get_twitter(conf):
    """ Read the config_file and construct an instance of TwitterAPI.
    Args:
      conf ... A config object name with Twitter credentials
    Returns:
      An instance of TwitterAPI.
    """
    twitter = TwitterAPI(
        conf.CONSUMER_KEY,
        conf.CONSUMER_SECRET,
        conf.ACCESS_TOKEN,
        conf.ACCESS_TOKEN_SECRET
    )
    return twitter

def show_config(conf):
    conf = getattr(config, conf)
    print('CONSUMER_KEY=%(CONSUMER_KEY)s\nCONSUMER_SECRET=%(CONSUMER_SECRET)s\nACCESS_TOKEN=%(ACCESS_TOKEN)s\nACCESS_TOKEN_SECRET=%(ACCESS_TOKEN_SECRET)s\n' % conf.__dict__)
    return

def robust_request(twitter, resource, params, timing, max_tries=5):
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
    while True:
        request = twitter.request(resource, params)
        if request.status_code == 200:
            return request
        else:
            timing.wait_nextwindow()
    return None

