import requests
import time
import random
import sys
import re
import json

#my files
from logger import logger

#Session settings
DEVICE_SETTINGS = {
    'manufacturer'      : 'Xiaomi',
    'model'             : 'HM 1SW',
    'android_version'   : 18,
    'android_release'   : '4.3'
}
USER_AGENT = 'Instagram 10.26.0 Android ({android_version}/{android_release}; 320dpi; 720x1280; {manufacturer}; {model}; armani; qcom; en_US)'.format(**DEVICE_SETTINGS)

#URLs
LOGIN_URL = "https://www.instagram.com/accounts/login/ajax/"
FOLLOW_URL = "https://www.instagram.com/web/friendships/%s/follow/"
UNFOLLOW_URL = "https://www.instagram.com/web/friendships/%s/unfollow/"
INBOX_URL = "https://www.instagram.com/direct_v2/inbox/"
HASHTAG_URL = "https://www.instagram.com/explore/tags/%s/?__a=1"
LIKE_URL = "https://www.instagram.com/web/likes/%s/like/"
COMMENT_URL = "https://www.instagram.com/web/comments/%s/add/"

class Bot(object):
    def __init__(self, username, password):
        self.username = username
        self.password = password
        #create a requests session to save cookies
        self.s = requests.Session()
        #logfile
        self.logfile = logger("logs/%s.log"%(self.username.replace(".","")))
        self.logfile.write("hello")
        self.login()
        
    def login(self):
        #try to log in
        self.logfile.write("%d: Trying to log in as %s...\n" % (time.time(), self.username))
        print("%d: Trying to log in as %s..." % (time.time(), self.username))
        self.s.cookies.update({
            'sessionid': '',
            'mid': '',
            'ig_pr': '1',
            'ig_vw': '1920',
            'csrftoken': '',
            's_netword': '',
            'ds_user_id': ''
        })
        login_post = {
            'username': self.username,
            'password': self.password
        }
        self.s.headers.update({
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'en-US',
            'Connection': 'keep-alive',
            'Content-Length': '0',
            'Host': 'www.instagram.com',
            'Origin': 'https://www.instagram.com',
            'Referer': 'https://www.instagram.com/',
            'User-Agent': USER_AGENT,
            'X-Instagram-AJAX': '1',
            'X-Requested-With': 'XMLHttpRequest'
        })
        r = self.s.get("https://www.instagram.com/")
        self.s.headers.update({'X-CSRFToken': r.cookies['csrftoken']})
        time.sleep(5*random.random())
        login = self.s.post(
            LOGIN_URL, data=login_post, allow_redirects=True)
        self.s.headers.update({'X-CSRFToken': login.cookies['csrftoken']})
        csrftoken = login.cookies['csrftoken']
        time.sleep(5 * random.random())
        if(login.status_code == 200):
            r = self.s.get("https://www.instagram.com/")
            finder = r.text.find(self.username)
            if(finder != -1):
                self.logfile.write("%d: apparently this was a success\n" % (time.time()))
                print("apparently this was a success")
            else:
                self.logfile.write("%d: I can't find the username in the response text\n" % (time.time()))
                print("I can't find the username in the response text")
                sys.exit()
        else:
            self.logfile.write("%d: response code was %d\n" % (time.time(), login.status.code))
            print("%d: response code was %d" % (time.time(), login.status.code))
            sys.exit()

    def follow(self, user_id):
        follow = self.s.post(FOLLOW_URL % (user_id))
        self.logfile.write("%d: Followed %s response: %s\n" % (time.time(), user_id, follow.text))
        print("%d: Followed %s response: %s" % (time.time(), user_id, follow.text))
    
    def unfollow(self, user_id):
        unfollow = self.s.post(UNFOLLOW_URL % (user_id))
        self.logfile.write("%d: Unfollowed %s response: %s\n" % (time.time(), user_id, unfollow.text))
        print("%d: Unfollowed %s response: %s" % (time.time(), user_id, unfollow.text))

    def like(self, media_id):
        like = self.s.post(LIKE_URL % (media_id))
        self.logfile.write("%d: liked %s response: %s\n" % (time.time(), media_id, like.text))
        print("%d: liked %s response: %s" % (time.time(), media_id, like.text))

    def comment(self, comment_text, media_id):
        comment = self.s.post(COMMENT_URL % (media_id), data={"comment_text":comment_text})
        self.logfile.write("%d: Commented %s on %s response: %s\n" %(time.time(), comment_text, media_id, comment.text))
        print("%d: Commented %s on %s response: %s" %(time.time(), comment_text, media_id, comment.text))
        
    def get_media_from_hashtag(self, hashtag):
        #scrape a hashtag for a list of media dicts. Keys I need to know: 'id' 'owner':'id'
        hashtag = self.s.post(HASHTAG_URL % (hashtag))
        return json.loads(hashtag.text)['tag']['media']['nodes']
