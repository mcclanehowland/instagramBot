import requests
import re

#get rid of annoying log message from requests library
import logging
logging.getLogger("requests").setLevel(logging.WARNING)

def get_follower(username):
    text = requests.get("https://www.instagram.com/"+username).text
    regex = '"followed_by": {"count": (\d+)}'
    followers = re.search(regex, text).group(1)
    if(followers is not None):
        return int(followers)

def get_following(username):
    text = requests.get("https://www.instagram.com/"+username).text
    regex = '"follows": {"count": (\d+)}'
    following = re.search(regex, text).group(1)
    if(following is not None):
        return int(following)
