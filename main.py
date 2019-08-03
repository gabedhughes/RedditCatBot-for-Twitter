#     * This program is free software. It comes without any warranty, to
#     * the extent permitted by applicable law. You can redistribute it
#     * and/or modify it under the terms of the Do What The Fuck You Want
#     * To Public License, Version 2, as published by Sam Hocevar. See
#     * http://www.wtfpl.net/ for more details.

import os
import time
import urllib
import requests

import praw as praw
import tweepy as tweepy


# Twitter API keys
ACCESS_TOKEN = ''
ACCESS_TOKEN_SECRET = ''
CONSUMER_KEY = ''
CONSUMER_SECRET = ''

# Reddit access tokens
REDDIT_CLIENT_ID = ''
REDDIT_CLIENT_SECRET = ''

# Multireddit to find posts from
MULTIREDDIT_USER = ''
MULTIREDDIT_NAME = ''

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


def setup_connection_reddit(multireddit_user, multireddit_name):
    print('[BOT] Setting up connection with Reddit')
    reddit_api = praw.Reddit(client_id=REDDIT_CLIENT_ID,
                             client_secret=REDDIT_CLIENT_SECRET,
                             user_agent='RedditCatBot by u/gdhughes5')
    return reddit_api.multireddit(multireddit_user,multireddit_name)


def tweet_creator(multireddit_info):
    post_dict = {}
    post_ids = []

    print('[BOT] Getting posts from Reddit')

    for submission in multireddit_info.hot(limit=5):
        if not already_tweeted(submission.id):
            post_dict[submission.title] = {}
            post = post_dict[submission.title]
            post['link'] = submission.permalink

            post['img_path'] = get_image(submission.url)

            post_ids.append(submission.id)
        else:
            print('[BOT] Already tweeted: {}'.format(str(submission)))

    return post_dict, post_ids


def already_tweeted(post_id):
    found = False
    with open(POSTED_CACHE, 'r') as in_file:
        for line in in_file:
            if post_id in line:
                found = True
                break
    return found


def strip_title(title, num_characters):
    if len(title) <= num_characters:
        return title
    else:
        return title[:num_characters - 1] + '…'


def get_image(img_url):
    file_name = os.path.basename(urllib.parse.urlsplit(img_url).path)
    img_path = IMAGE_DIR + '/' + file_name
    print('[BOT] Downloading image at URL ' + img_url + ' to ' + img_path)
    resp = requests.get(img_url, stream=True)
    if resp.status_code == 200:
        with open(img_path, 'wb') as image_file:
            for chunk in resp:
                image_file.write(chunk)
        return img_path
    else:
        print('[bot] Image failed to download. Status code: ' + resp.status_code)
    return ''


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

    multireddit = setup_connection_reddit(MULTIREDDIT_USER, MULTIREDDIT_NAME)
    post_dict, post_ids = tweet_creator(multireddit)
    #tweeter(post_dict,post_ids)

    #for filename in globals(IMAGE_DIR + '/*'):
    #    os.remove(filename)


if __name__ == '__main__':
    main()
