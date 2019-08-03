#     * This program is free software. It comes without any warranty, to
#     * the extent permitted by applicable law. You can redistribute it
#     * and/or modify it under the terms of the Do What The Fuck You Want
#     * To Public License, Version 2, as published by Sam Hocevar. See
#     * http://www.wtfpl.net/ for more details.

import os

# Twitter API keys
import time

import tweepy as tweepy

ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

# Multireddit to find posts from
MULTIREDDIT_TO_MONITOR = ''

# Directory to download images to
IMAGE_DIR = 'img'

# Keep a cache to prevent reposts (from the bot, Redditors are gonna repost)
POSTED_CACHE = 'posted.txt'

# Put this at the end of every Tweet
TWEET_SUFFIX = ''

# Maximum tweet length (if Twitter ever decides to change this again)
TWEET_MAX_LENGTH = 280

# Delay between Tweets (in sec)
DELAY_BETWEEN_TWEETS = 3600

# Length of t.co links (More info: https://dev.twitter.com/overview/t.co)
T_CO_LINKS_LEN = 24


def tweeter(post_dict, post_ids):
    auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
    auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
    api = tweepy.API(auth);

    for post, post_id in zip(post_dict, post_ids):
        img_path = post_dict[post]['img path']

        extra_text = ' ' + post_dict[post]['link'] + TWEET_SUFFIX
        extra_text_len = 1 + T_CO_LINKS_LEN + len(TWEET_SUFFIX)
        if img_path:
            extra_text_len += T_CO_LINKS_LEN
        post_text = strip_title(post, TWEET_MAX_LENGTH - extra_text_len) + extra_text
        print('[BOT] Posting this link on Twitter')
        print(post_text)
        if img_path:
            print('[BOT] with image ' + img_path)
            api.update_with_media(filename=img_path, status=post_text)
        else:
            api.update_status(status=post_text)
        log_tweet(post_id)
        time.sleep(DELAY_BETWEEN_TWEETS)


def log_tweet(post_id):
    with open(POSTED_CACHE, 'a') as out_file:
        out_file.write(str(post_id) + '\n')


def main():
    if not os.path.exists(POSTED_CACHE):
        with open(POSTED_CACHE, 'w'):
            pass
    if not os.path.exists(IMAGE_DIR):
        os.makedirs(IMAGE_DIR)

    multireddit = setup_connection_reddit(multireddit)
    post_dict, post_ids = tweet_creator(multireddit)
    tweeter(post_dict,post_ids)

    for filename in globals(IMAGE_DIR + '/*'):
        os.remove(filename)


if __name__ == '__main__':
    main()
