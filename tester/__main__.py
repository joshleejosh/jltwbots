# Tester is a read-only script to help make sure we can communicate with twitter.

import argparse
import jltw

def test_me(fn, q):
    api = jltw.open_twitter(fn)
    #tweets = api.GetUserTimeline()
    #print api.VerifyCredentials().screen_name
    tweets = api.GetSearch('q='+q, count=200)
    for tweet in tweets:
        s = '%s: %s'%(tweet.user.screen_name, tweet.text)
        print s.encode('utf-8')

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials')
    parser.add_argument('searchstring', type=str, help='A string to search for')
    args = parser.parse_args()
    test_me(args.authfile, args.searchstring)

