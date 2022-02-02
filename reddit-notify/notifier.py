import praw
from pushbullet import Pushbullet
import time

token = 'o.5UJF58DGMRWCkEctD0NFw4mz6AaWTFzb'

pb = Pushbullet(token)

reddit = praw.Reddit(client_id='sy5zBbkC8uUcHQ',
                     client_secret='xDAe23dqN5ZhJZlYjg82WBgSFfw', user_agent='PRAW autobot for notifications')

subreddit = reddit.subreddit('lego_raffles')

last_check = time.time()

print(subreddit.display_name)

while True:
    for post in subreddit.new():
        if post.created_utc > last_check - 60 * 10:
            pb.push_link(post.title, post.permalink)
            print('Pushing', post.title)
        else:
            continue

    last_check = time.time()
    print('Passed check')
    time.sleep(60 * 10)
