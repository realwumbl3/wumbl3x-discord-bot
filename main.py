import discord
from discord.ext import commands
import logging
from flask import Flask, redirect
from threading import Thread
import requests
import json
import re
import os

root = logging.getLogger()
logger = logging.basicConfig(
    level=logging.INFO,
    filename="logging/bot.log",
    filemode="a+",
    format="%(filename)s - %(lineno)d - %(levelname)s %(asctime)s - %(message)s",
)


from zyXserve.globe import gSetter

from flask import Flask, request, make_response
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address


app = Flask(__name__)
gSetter(app=app)


def BLK_CTR_TXT(txt):
    return f"""<div style="position:absolute;inset:0;background:black;color:white;display:grid;place-items:center;font-family:arial;">{txt}</div>"""


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri="memory://",
    on_breach=lambda x: make_response(
        BLK_CTR_TXT("You are not allowed to access this resource this often, please wait."),
        200,
    ),
)

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.messages = True
intents.typing = True
intents.message_content = True

discord_client = discord.Client(intents=intents)

command_client = commands.Bot(command_prefix="!", intents=intents)

gSetter(discord_client=discord_client, command_client=command_client)

logging.info("Starting bot...")


############################################# INVITE LINK #############################################

from modules.region_database import get_visitor_data


@app.route("/")
@limiter.limit("6 per minute")
def index():
    get_visitor_data(request)
    return redirect("https://discord.gg/Mzwz8WzuUZ")


######################################### ROLE SELECTOR #########################################

from modules.role_selector import Role, RoleSelector

role_selector = RoleSelector(
    discord_client, roles_channel_id=938339346292019230, roles_msg_id=1086128572625846282
)


role_selector.add_roles(
    Role("NSFW", 938338119143542834, "💘"),
    Role("BEBEH", 919752389626560552, "🍼"),
    Role("NOTIFS", 1086405926841503845, "🔔"),
    Role("DEV", 1086405597974507571, "💻"),
    Role("ARTIST", 1086412445423243338, "🎨"),
)


############################################# JOINLEAVE #############################################

from modules.join_leave import JoinLeaveBot

join_leave_bot = JoinLeaveBot(
    discord_client,
    join_leave_channel=1088972386310815764,
    server_alias="Chroma's Holodeck Fungeon!",
)

############################################# TWITTER LIKES #############################################


from modules.twitter_webhook import app, add_like_by_id


@command_client.command()
async def add_like(ctx, msg_content=None):
    message_id = ctx.message.id
    # find tweet id using re, could be a tweet url or just the id
    tweet_id = re.search("([\d]{10,20})", msg_content).group(1)
    if not tweet_id:
        await ctx.send("Invalid tweet id.")
        return
    authod_id = ctx.message.author.id
    if authod_id != 163228516450697216:
        # remove the message
        logging.info(f"Removing message: id[{message_id}]")
        await ctx.message.delete()
        return
    add_like_by_id(tweet_id)
    logging.info(f"Adding like: id[{message_id}] tweet_id[{tweet_id}] content[{msg_content}]")


############################################# INIT DISCORD #############################################


@discord_client.event
async def on_ready():
    logging.info(f"[discord_client] {discord_client.user} has connected to Discord!")


@command_client.event
async def on_ready():
    logging.info(f"[command_client] {command_client.user} has connected to Discord!")


DISCORD_TOKEN = os.environ.get("DISCORD_TOKEN", None)

if DISCORD_TOKEN is None:
    print("DISCORD_TOKEN not found in environment variables")
    logging.error("DISCORD_TOKEN not found in environment variables")
    exit(1)

logging.info("Starting discord bot with token: " + DISCORD_TOKEN)

discord_bot_thread = Thread(target=discord_client.run, args=(DISCORD_TOKEN,), daemon=True)
discord_command_thread = Thread(target=command_client.run, args=(DISCORD_TOKEN,), daemon=True)

logging.info("Starting discord bot")
discord_bot_thread.start()

logging.info("Starting command bot")
discord_command_thread.start()
