import requests
import praw
import pandas as pd
import datetime


# function to find all ticker symbols in a string
# will return a list of all strings of 3-5 uppercase characters
# we'll have to come up with a strategy for filtering out people's all-caps shit-posting
def filter_for_stocks(c):
    i = 0
    stocks = []
    while i < len(c):
        if c[i].islower() and not c[i] == '.':
            i = i + 1
        else:
            stock = ''
            valid = True
            for j in range(i, min(i+5, len(c))):
                if c[j].islower() or not c[j].isalpha():
                    i = j + 1
                    valid = False
                    break
                else:
                    stock = stock + c[j]
            if len(stock) >= 3 and not blacklisted_stocks(stock):
                stocks.append(stock)
            if valid:
                i = i + len(stock)
    return stocks


# Pulls reddit data and sorts through it
def reddit_scrape(isUSA):
    only_save_comments_with_stocks_mentioned = True
    reddit = praw.Reddit(client_id='KNCL9KcMWlKblg',
                         client_secret='UF_6u4tZjUU7d0NrpaN9mG0senJBsA',
                         user_agent='TestApp for u/reddit_api_account',
                         username='reddit_api_account',
                         password='cashmoney')

    subreddits_to_scrape = ['CanadianInvestor', 'PersonalFinanceCanada']
    if isUSA:
        subreddits_to_scrape = ['wallstreetbets', 'stocks', 'personalfinance', 'investing']

    comments_dict = {"author": [],
                     "body": [],
                     "score": [],
                     "permalink": [],
                     "submission_id": [],
                     "submission_title": [],
                     "submission_rank": [],
                     "mentions_stocks": [],
                     "created": []}
    stocks_mentioned = []

    for sub_name in subreddits_to_scrape:
        subreddit = reddit.subreddit(sub_name)
        count = 0
        rank = 1
        for submission in subreddit.hot(limit=8):
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

                stocks = filter_for_stocks(c.body)
                if len(stocks):
                    # print(stocks)
                    stocks_mentioned = stocks_mentioned + stocks
                    has_stocks_mentioned = True

                if has_stocks_mentioned or not only_save_comments_with_stocks_mentioned:
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

    if isUSA:
        comments_data.to_csv('COMMENT_DATA_' + str(datetime.date.today()) + '.csv', index=False)
    else:
        comments_data.to_csv('CAN_COMMENT_DATA_' + str(datetime.date.today()) + '.csv', index=False)

    print_limit = 10
    if not isUSA:
        print_limit = 3
    stocks_dict = {"stock": [],
                   "times_mentioned": []}
    for s in stocks_mentioned:
        if stocks_dict['stock'].count(s) == 0:
            stocks_dict['stock'].append(s)
            stocks_dict['times_mentioned'].append(stocks_mentioned.count(s))
    for i in range(len(stocks_dict['stock'])):
        if stocks_dict['times_mentioned'][i] > print_limit:
            print(stocks_dict['stock'][i] + ' was seen ' + str(stocks_dict['times_mentioned'][i]) + ' times')
    stocks_data = pd.DataFrame(stocks_dict)
    if isUSA:
        stocks_data.to_csv('STOCK_DATA_' + str(datetime.date.today()) + '.csv', index=False)
    else:
        stocks_data.to_csv('CAN_STOCK_DATA_' + str(datetime.date.today()) + '.csv', index=False)


def blacklisted_stocks(stock):
    blacklist = ['ETF', 'IPO', 'YOLO', 'THE', 'EDIT',
                 'EOW', 'WSB', 'STEM', 'CERB', 'CRA',
                 'TFSA', 'TSX', 'IRA', 'IRS',
                 'HOA', 'CCP', 'FUCK', 'BUY',
                 'HOLD', 'CEO', 'FUCKI', 'HHHHH',
                 'LETS', 'GANG']
    if blacklist.count(stock):
        return True
    return False


reddit_scrape(True)
reddit_scrape(False)
