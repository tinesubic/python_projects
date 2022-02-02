import praw
from pushbullet import Pushbullet
import json

apikey="o.b12sGUFkUfKA4Q5XlwIZa3hOANluOgMR"

pbcli = Pushbullet(apikey)

# pbcli.push_link("New reddit post", "https://reddit.com")


reddit = praw.Reddit(client_id="lTKBMsLPMF4v4Q", client_secret="wWILDe9l6_F6PF5phKR34c5WQ4Q", user_agent="test-tine")

config = {}
with open("./config.json", 'r') as infile:
    config = json.load(infile)

for sub in config:
    for submission in reddit.subreddit(sub).new(limit=10):
        print(submission.title)