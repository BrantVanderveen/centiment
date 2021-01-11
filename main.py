import requests
import praw
import pandas as pd


# function to find all ticker symbols in a string
# will return a list of all strings of 3-5 uppercase characters
# we'll have to come up with a strategy for filtering out people's all-caps shit-posting
def filter_for_stocks(c):
    i = 0
    tickers = []
    while i < len(c):
        if c[i].islower() and not c[i] == '.':
            i = i + 1
        else:
            ticker = ''
            valid = True
            for j in range(i, min(i+5, len(c))):
                if c[j].islower() or not c[j].isalpha():
                    i = j + 1
                    valid = False
                    break
                else:
                    ticker = ticker + c[j]
            if len(ticker) >= 3:
                tickers.append(ticker)
            if valid:
                i = i + len(ticker)
    return tickers


# Pulls reddit data and sorts through it
def reddit_scrape():
    reddit = praw.Reddit(client_id='KNCL9KcMWlKblg',
                         client_secret='UF_6u4tZjUU7d0NrpaN9mG0senJBsA',
                         user_agent='TestApp for u/reddit_api_account',
                         username='reddit_api_account',
                         password='cashmoney')

    subreddit = reddit.subreddit('wallstreetbets')

    comments_dict = {"author": [],
                     "body": [],
                     "score": [],
                     "permalink": [],
                     "submission_id": [],
                     "submission_title": [],
                     "submission_rank": [],
                     "mentions_stocks": [],
                     "created": []}
    count = 0
    rank = 1
    for submission in subreddit.hot(limit=3):
        post = reddit.submission(submission.id)
        print('submission: ', submission.title)
        comments = post.comments
        print('comments retrieved')
        comments.replace_more(1)
        print('comments expanded')
        for c in comments.list():
            has_stocks_mentioned = False
            if count >= 100:
                break
            count = count + 1

            tickers = filter_for_stocks(c.body)
            if len(tickers):
                print(tickers)
                has_stocks_mentioned = True

            comments_dict["author"].append(c.author)
            comments_dict["body"].append(c.body)
            comments_dict["score"].append(c.score)
            comments_dict["permalink"].append(c.permalink)
            comments_dict["created"].append(c.created_utc)
            comments_dict["submission_id"].append(submission.id)
            comments_dict["submission_title"].append(submission.title)
            comments_dict["submission_rank"].append(str(rank))
            if has_stocks_mentioned:
                comments_dict["mentions_stocks"].append("Yes")
            else:
                comments_dict["mentions_stocks"].append("No")

        count = 0
        rank = rank + 1

    comments_data = pd.DataFrame(comments_dict)


reddit_scrape()