# jltw: utility functions for communicating with twitter

import json, twitter

def log(*args):
    print (u' '.join(map(unicode, args))).encode('utf-8')

def open_twitter(authfn):
    fp = open(authfn)
    authd = json.load(fp)
    fp.close()
    api = twitter.Api(consumer_key=authd['consumer_key'],
            consumer_secret=authd['consumer_secret'],
            access_token_key=authd['token_key'],
            access_token_secret=authd['token_secret']
            )
    return api

