import logging
from threading import Thread

logging.info("Starting Twitter webhook...")


from datetime import datetime
from time import sleep
import base64
import hashlib
import hmac
from re import search
import os
import json
from itertools import cycle
from collections import deque

from zyxPy.json.FastJsonStore import FastJsonStore

HOT_CONFIG = FastJsonStore("hotConfig.json")


from pyTwitterAccount.v1_4 import STweet, pyTwiAccount, TweetParse

APP_DATA = "/home/wumbl3vps/Data-23/alphaDek/TweetFeed"

ACCOUNTS_ROOT = f"{APP_DATA}/accounts"
STWEET_DB_FILE = f"{APP_DATA}/sTweet-8.db"
TWEET_CREDS = f"{APP_DATA}/twitterAPICredentials.json"

pyTwiAccount.set_root(ACCOUNTS_ROOT)
wumbl3_account = pyTwiAccount.TwitterAccount(handle="wumbl3")
STWEET = STweet.STweet(accounts_root=ACCOUNTS_ROOT, stweet_db_file=STWEET_DB_FILE)

import asyncio

from zyXserve.globe import discord_client as d_client, app

from flask import Flask, request, make_response

app = app  # type: Flask

from discord import Client as DiscordClient, Embed as DiscordEmbed, Object as DiscordObject

discord_client = d_client  # type: DiscordClient

from zyXserve.v1_3.Sqlite import SqliteDatabase, orm, sql

likes_database = SqliteDatabase({"db_path": f"db/likes.db", "overwrite": False})


class Like(likes_database.base):
    __tablename__ = "likes"
    id = sql.Column(sql.Integer, primary_key=True)
    created_at = sql.Column(sql.DateTime, default=datetime.utcnow)
    tweet_id = sql.Column(sql.String(20))
    message_id = sql.Column(sql.String(20))
    ok = sql.Column(sql.Boolean, default=True)
    status = sql.Column(sql.String(100), default="ok")


likes_database.create_all()

VERBOSE = False

COLOR_NEXT = cycle(["F51CFF", "1CFCFF", "FCFF25"]).__next__
COLOR_CYCLE = lambda: int(COLOR_NEXT(), 16)
LOGO_CYCLE = cycle(["yellow.png", "magenta.png", "cyan.png"]).__next__

SENT_TWEETS = deque(maxlen=100)


def await_in_another_thread(coroutine):
    try:
        Thread(target=lambda: asyncio.run(coroutine)).start()
    except Exception as e:
        logging.exception(e)


# @app.route("/webhooks/twitter", methods=["POST"])
# def twitter_activity_webhook():
#     logging.info("Twitter webhook called.")
#     request_json = request.get_json()
#     if "favorite_events" in request_json:
#         tweet_json = request_json["favorite_events"][0]["favorited_status"]
#     else:
#         return make_response("thanks 😎", 200)
#     if "extended_tweet" in tweet_json:
#         tweet_json.update(tweet_json["extended_tweet"])
#     await_in_another_thread(discord_webhook(tweet_json))
#     VERBOSE and logging.info("Returning 200 to twitter.")
#     return make_response("thanks 😎", 200)


def create_embeds(tweetParse):
    tweet = tweetParse.tweet
    tweet_id = tweet.id
    artist = tweet.user.handle
    pfp = tweet.user.pfp
    twtr = tweetParse.twtr

    tweet_created_at = datetime.strptime(tweet.creation, "%a %b %d %H:%M:%S %Y").isoformat()

    embeds = []

    if hasattr(tweet, "text"):
        tweet_text = tweet.text
    else:
        tweet_text = ""

    if tweet.media.type == "image" or tweet.media.type == "images":
        for item in tweet.media.variants:
            embeds.append(
                {"url": f"https://twitter.com/i/status/{tweet_id}", "image": {"url": item}}
            )
    elif tweet.media.type == "video" or tweet.media.type == "gif":
        cover = tweet.media.cover
        video = tweet.media.variants[-1].split("?")[0]
        embeds.append(
            {
                "url": f"https://twitter.com/i/status/{tweet_id}",
                "image": {"url": cover},
                "video": {"url": video},
            }
        )
        tweet_text += f"\n\n[open video in browser]({video})"

    embeds[0].update(
        {
            "title": f"twitter@{artist}:{tweet_id}",
            "url": f"https://twitter.com/i/status/{tweet_id}",
            "color": COLOR_CYCLE(),
            "description": tweet_text,
            "timestamp": tweet_created_at,
            "author": {
                "name": f"By @{artist}",
                "url": f"https://twitter.com/{artist}",
                "icon_url": twitter_pfp(pfp),
            },
            "footer": {
                "text": f"twitter",
                "icon_url": "https://discord.wumbl3.xyz/assets/" + LOGO_CYCLE(),
            },
        }
    )

    return {
        "embeds": embeds,
        "twtr": twtr,
    }


async def discord_webhook(tweet_json, check=True):
    VERBOSE and logging.info("")
    VERBOSE and logging.info(f"New Tweet Liked!")
    VERBOSE and logging.info(f"tweet_json: {json.dumps(tweet_json)}")

    session = likes_database.create_session()
    database_entry = None

    try:
        tweetParse = TweetParse.TweetParse(tweet_json)

        tweet = tweetParse.tweet

        if not hasattr(tweet, "media"):
            VERBOSE and logging.info("No media in tweet skipping...")
            return None

        tweet_id = tweet.id

        database_entry = Like(tweet_id=tweet_id)
        database_entry.status = "Starting delay."

        if check:
            DELAY = HOT_CONFIG.get("TwitterLikeDelay", 0)
            VERBOSE and logging.info(f"Checking if tweet is still liked... in {DELAY} seconds")
            sleep(DELAY)

            if tweet_id in SENT_TWEETS:
                VERBOSE and logging.info("Tweet already processed skipping...")
                return None

            current_tweet_data = STWEET.getStweetJsonByID(tweet_id)

            if current_tweet_data["favorited"] == False:
                VERBOSE and logging.info("Tweet no longer liked skipping...")
                database_entry.status = (
                    f"Tweet was unliked before the {DELAY} second delay and was skipped."
                )
                return None

            SENT_TWEETS.appendleft(tweet_id)

        database_entry.status = "Creating embeds."

        embeds = create_embeds(tweetParse)

        twtr = embeds["twtr"]

        database_entry.status = "Embeds created."

        channel = discord_client.get_channel(1086791877308727368)

        VERBOSE and logging.info("Sending to discord channel...")
        VERBOSE and logging.info("embeds: " + json.dumps(embeds))
        VERBOSE and logging.info("channel: " + str(channel))

        database_entry.status = "Sending to discord channel. (not complete)"

        send = ioawait(
            channel.send(
                content=f"New Tweet Liked By twitter@{twtr}!",
                embeds=[DiscordEmbed.from_dict(e) for e in embeds["embeds"]],
            )
        )
        results = send.result()

        if not results:
            database_entry.status = (
                "Message was not sent to the discord channel. (unknown error with discord)"
            )
            raise Exception("Message was not sent to the discord channel.")

        database_entry.message_id = results.id
        database_entry.status = "Tweet was sent to the discord channel."

        #  add heart and retweet reactions
        ioawait(results.add_reaction("❤️"))

        VERBOSE and logging.info("Sent to discord channel!")
        VERBOSE and logging.info(results)
    except Exception as e:
        if database_entry:
            database_entry.ok = False
        logging.error("Exception in discord_webhook")
        logging.exception(e)
        logging.error("")
    finally:
        VERBOSE and logging.info("")
        if database_entry:
            safelyAddToDatabase(session, database_entry)


def remove_message_by_tweet_id(tweet_id):
    try:
        session = likes_database.create_session()

        messages = session.query(Like).filter(Like.tweet_id == tweet_id).all()
        if not messages:
            return {"error": "No message found with that tweet id."}

        channel = discord_client.get_channel(1086791877308727368)
        results = ioawait(
            channel.delete_messages(
                [DiscordObject(id=m.message_id) for m in messages if m.message_id]
            )
        )

        VERBOSE and logging.info(results)

        for m in messages:
            m.status = "Message was deleted from the discord channel."

        session.commit()

        return {"ok": "Message was deleted from the discord channel."}

    except Exception as e:
        logging.error("Exception in remove_message_by_id")
        logging.exception(e)
        logging.error("")
        return {"error": "Exception in remove_message_by_id"}
    finally:
        session.close()


def check_sec_key(post_data):
    env_sec_key = os.environ["SECRET"]
    post_sec_key = post_data.get("secret", None)
    if not post_sec_key:
        return make_response({"error": "No secret provided."}, 200)

    if post_sec_key != env_sec_key:
        return make_response({"error": f"Inval secret, it starts w/ '{env_sec_key[:5]}'"}, 200)

    return False


@app.route("/remove_like", methods=["POST"])
def remove_like():
    try:
        logging.info("remove_like")
        post_data = request.get_json()

        if key_check := check_sec_key(post_data):
            return key_check

        tweet_id = post_data.get("tweet_id", None)
        if not tweet_id:
            return make_response({"error": "No tweet_id provided."}, 200)

        return make_response(remove_message_by_tweet_id(tweet_id), 200)
    except Exception as e:
        logging.error("Exception in remove_like")
        logging.exception(e)


# @app.route("/add_like", methods=["POST"])
# def add_like():
#     try:
#         post_data = request.get_json()
#         if key_check := check_sec_key(post_data):
#             return key_check
#         tweet_id = post_data.get("tweet_id", None)
#         if not tweet_id:
#             return make_response({"error": "No tweet_id provided."}, 200)
#         if "twitter.com" in tweet_id:
#             tweet_id = search(r"status/(\d+)", tweet_id).group(1)
#         return make_response(add_like_by_id(tweet_id), 200)
#     except Exception as e:
#         logging.error("Exception in remove_like")
#         logging.exception(e)


@app.route("/add_like_by_stweet", methods=["POST"])
def add_like_by_stweet():
    try:
        post_data = request.get_json()

        if key_check := check_sec_key(post_data):
            return key_check

        tweet_id = post_data.get("tweet_id", None)

        if not tweet_id:
            return make_response({"error": "No tweet_id provided."}, 200)

        if "twitter.com" in tweet_id:
            tweet_id = search(r"status/(\d+)", tweet_id).group(1)

        return make_response(add_like_by_stweet(tweet_id), 200)
    except Exception as e:
        logging.error("Exception in remove_like")
        logging.exception(e)


def add_like_by_stweet(tweet_id):
    try:
        stweet_json = STWEET.getStweetJsonByID(tweet_id)
        if not stweet_json:
            raise Exception("No stweet json found.")
        await_in_another_thread(discord_webhook(stweet_json, check=True))
        return {"ok": "Tweet was sent to the discord channel. (maybe)"}
    except Exception as e:
        logging.error("Exception in add_like_by_id")
        logging.exception(e)
        return {"error": "Exception in add_like_by_id"}


# def add_like_by_id(tweet_id):
#     try:
#         tweet_json = wumbl3_api_v1.get_status(tweet_id, tweet_mode="extended")
#         tweet_json = tweet_json._json
#         await_in_another_thread(discord_webhook(tweet_json, check=False))
#         return {"ok": "Tweet was sent to the discord channel. (maybe)"}
#     except Exception as e:
#         logging.error("Exception in add_like_by_id")
#         logging.exception(e)
#         return {"error": "Exception in add_like_by_id"}


def ioawait(coroutine):
    return asyncio.run_coroutine_threadsafe(coroutine, discord_client.loop)


def safelyAddToDatabase(session, database_entry):
    try:
        session.add(database_entry)
        session.commit()
    except Exception as e:
        logging.error("Exception in safelyAddToDatabase")
        logging.exception(e)
        logging.error("")
        session.rollback()
    finally:
        session.close()


def twitter_pfp(pfp):
    return (
        "https://abs.twimg.com/sticky/default_profile_images/default_profile_normal.png"
        if pfp == "default"
        else f"https://pbs.twimg.com/profile_images/{pfp}"
    )


# # Defines a route for the GET request
# @app.route("/webhooks/twitter", methods=["GET"])
# async def webhook_challenge():
#     try:
#         logging.info("webhook challenge")
#         consumer_secret = os.environ["consumer_secret"].encode("utf-8")
#         crc_token = request.args.get("crc_token").encode("utf-8")

#         sha256_hash_digest = hmac.new(
#             consumer_secret, msg=crc_token, digestmod=hashlib.sha256
#         ).digest()
#         # construct response data with base64 encoded hash
#         response = {
#             "response_token": "sha256=" + base64.b64encode(sha256_hash_digest).decode("utf-8")
#         }
#         logging.info("Webhook challenge response: ")
#         logging.info(response)
#         # returns properly formatted json response
#         return json.dumps(response)
#     except Exception as e:
#         logging.error("Error in webhook_challenge")
#         logging.exception(e)


# logging.info("Twitter webhook started!")
