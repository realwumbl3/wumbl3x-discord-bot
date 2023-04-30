from pyTwitterAccount.v1_4 import STweet, pyTwiAccount, TweetParse

APP_DATA = "/home/wumbl3vps/Data-23/alphaDek/TweetFeed"

ACCOUNTS_ROOT = f"{APP_DATA}/accounts"
STWEET_DB_FILE = f"{APP_DATA}/sTweet-8.db"
TWEET_CREDS = f"{APP_DATA}/twitterAPICredentials.json"

pyTwiAccount.set_root(ACCOUNTS_ROOT)
wumbl3_account = pyTwiAccount.TwitterAccount(handle="wumbl3")
STWEET = STweet.STweet(accounts_root=ACCOUNTS_ROOT, stweet_db_file=STWEET_DB_FILE)

print(TWEET_CREDS)
mainTwitterApi = pyTwiAccount.init_main_api(TWEET_CREDS)

print(mainTwitterApi.list_webhooks())
