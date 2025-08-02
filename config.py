import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "21883290"))
API_HASH = getenv("API_HASH", "d58e9d672b9cbbe8d6c3d3fa0d0546e9")
BOT_TOKEN = getenv("BOT_TOKEN", "7399017823:AAHMF85X6WeCcr_JY2A_IARgXfL80laD7qI")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://knight4563:knight4563@cluster0.a5br0se.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1000000))
LOGGER_ID = int(getenv("LOGGER_ID", "-1002823976818"))
OWNER_ID = int(getenv("OWNER_ID", "8473985518"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/itzarjuna1/Gx-pro-musicbot")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/+wD3_dWkCkSYzMWE1")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/+SKnKWWIEIDw3MGEx")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

STRING1 = getenv("STRING_SESSION", "AQFN6ZoALLm-WfXZxh-rFTu5Ow-kyHuONC_UhozKXDXoE-1SXqrpsCOeL02oKDA45gwXJr_j7l0M5GgLuDcZcum743XLB332D1JBQgmQZ2JjX4FstCl-E7iDh62rawrAOrzoZJsg3X_1vjXE6JWkwXuKRvV0_COk2_6kqdE4V0liPryPxH9yMyNrDwPcOPmzQvJZkZmwvUcWtG_FXnCykEQEN9Se-kG5SVbeRZ_b--DRAffNVoyfB-e2bRfuRMqKVnH9UnScXP0TMVBz_2QoteOosaQsjWvgU7gjBnKdvvdhEvoHyeOHtd1xts2vy8eTDmCvu8u-dKWFJdT51xad2q9yyGM0AQAAAAHRpZTBAA")
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
