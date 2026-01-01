import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "35279715"))
API_HASH = getenv("API_HASH", "b4c339216397b5941d88c8617d2dc12b")
BOT_TOKEN = getenv("BOT_TOKEN", "")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://knight4563:knight4563@cluster0.a5br0se.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1000000))
LOGGER_ID = int(getenv("LOGGER_ID", "-1003468243393"))
OWNER_ID = int(getenv("OWNER_ID", "7651303468"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/itzarjuna1/Gx-pro-musicbot")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/dark_musictm")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/snowy_support")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", false))

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

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/8v3sw6.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/8v3sw6.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
STATS_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/8v3sw6.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/8v3sw6.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/8v3sw6.jpg"

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
