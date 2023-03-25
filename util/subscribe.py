import logging
import os
import json


try:
    with open("secrets.json", "r") as f:
        json_data = json.load(f)
        for key, value in json_data.items():
            os.environ[key] = value
except Exception as e:
    logging.exception(e)

from twitivity import Activity

account_activity = Activity()


def subscribe_to_twitter_webhook():
    # Subscribe to webhook
    logging.info("Subscribing to webhook:")
    sub = account_activity.register_webhook("https://discord.wumbl3.xyz/webhooks/twitter")
    print(sub)
    logging.info(sub)
    logging.info(account_activity.subscribe())
 

def unsub():
    # Remove subscription refresh('webhookID')
    unsub = account_activity.delete("1460158551163383809")
    print(unsub)
    logging.info("Unsubscribing from webhook:")
    logging.info(unsub)


def list_webhooks():
    # List subscribed webhooks
    webhooks = account_activity.webhooks()
    logging.info("List subscribed webhooks:")
    logging.info(webhooks)
    print(webhooks)


# unsub()
# list_webhooks()
subscribe_to_twitter_webhook()
