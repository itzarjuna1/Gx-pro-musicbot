import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters
import telegram.ext as tg
from pyrogram import Client
import logging  
from telegram.ext import Application

from motor.motor_asyncio import AsyncIOMotorClient

load_dotenv()

API_ID = int(getenv("API_ID", "39679517"))
API_HASH = getenv("API_HASH", "aed61e5ff8c711895f8b0c99e51c16cc")
BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://knight4563:knight4563@cluster0.a5br0se.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1000000))
LOGGER_ID = int(getenv("LOGGER_ID", "-1003882647583"))
OWNER_ID = int(getenv("OWNER_ID", "8364692780"))
SUDO_USERS = list(map(int, os.getenv(
    "SUDO_USERS",
    "8569102770,8285730532,8364692780"
).split(",")))
BOT_USERNAME = os.getenv("BOT_USERNAME", "waifuxmusicbot")
IMG_URL = os.getenv("IMG_URL", "https://files.catbox.moe/376q7n.jpg").split()
UPDATE_CHAT = os.getenv("UPDATE_CHAT", "-1003882647583")
CHANNEL_ID = os.getenv("CHANNEL_ID", "-1003729074782")


HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/itzarjuna1/Gx-pro-musicbot")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/theinfinitynetwork")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/theinfinity_suppport")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", False))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

STRING1 = getenv("STRING_SESSION", "")
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)

BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}

client = AsyncIOMotorClient(MONGO_DB_URI)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/8fdj9b.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/8fdj9b.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
STATS_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/8fdj9b.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/8fdj9b.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/8fdj9b.jpg"

application = Application.builder().token(BOT_TOKEN).build()
Loy = Client(
    "Espro",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    
    
)

def time_to_seconds(time):
    stringt = str(time)
    return sum(int(x) * 60**i for i, x in enumerate(reversed(stringt.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

if SUPPORT_CHANNEL:
    if not re.match("(?:http|https)://", SUPPORT_CHANNEL):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHANNEL url is wrong. Please ensure that it starts with https://"
        )

if SUPPORT_CHAT:
    if not re.match("(?:http|https)://", SUPPORT_CHAT):
        raise SystemExit(
            "[ERROR] - Your SUPPORT_CHAT url is wrong. Please ensure that it starts with https://"
        )
