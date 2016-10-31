# Tester is a read-only script to help make sure we can communicate with twitter.

import argparse
import jltw

def test_me(fn):
    api = jltw.open_twitter(fn)
    tweets = api.GetUserTimeline()
    print api.VerifyCredentials().screen_name
    for tweet in tweets:
        print tweet.text

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('authfile', type=str, help='File containing Twitter credentials')
    args = parser.parse_args()
    test_me(args.authfile)

