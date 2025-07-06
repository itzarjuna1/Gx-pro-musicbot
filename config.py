import re
from os import getenv

from dotenv import load_dotenv
from pyrogram import filters

load_dotenv()

API_ID = int(getenv("API_ID", "12565317"))
API_HASH = getenv("API_HASH", "de3e1a800e0ebdff1031232be6c38814")
BOT_TOKEN = getenv("BOT_TOKEN", "7597057529:AAG4TvzqXvlT3hSxddwXatGGvdmkyBcdlm0")
MONGO_DB_URI = getenv("MONGO_DB_URI", "mongodb+srv://knight4563:knight4563@cluster0.a5br0se.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", 1000000))
LOGGER_ID = int(getenv("LOGGER_ID", "-1002881119599"))
OWNER_ID = int(getenv("OWNER_ID", "7926944005"))

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/itzarjuna1/Gx-pro-musicbot.git")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/dark_x_knight_musiczz_support")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/dark_knight_support")

AUTO_LEAVING_ASSISTANT = bool(getenv("AUTO_LEAVING_ASSISTANT", True))

SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", None)
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", None)

PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", 25))

TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", 104857600))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", 1073741824))

STRING1 = getenv("STRING_SESSION", "BQC_u0UAgry1rt397-lBLrs0iTIo6qqrWuhWTlSpEJ8wofA2vhtV89iegnE-d-EwkAomjLrKQFxhhDS6WZZzyoOXOvF3DyWT8sltXMoB6w9654wEakOMJ1Q32Vmumxwi-R_rL0z0Gk6JQ5WQ7oC2msJIA0Vpo1Y_XBcHrlUCt0a9uuDlUnN0tfLQmQEW12wpODw_Fj_TkxCSH5LAIsvxoVmVoRab1A7qfuDpkpmeZq5RLG7vlCqCLv7ldVOugg1ka81mpki9lLwJ2l8PxHioVtomgTu5OdLTbQK-xpyqEqyEhJH_2cC6kisM2Q08g0i-6a7RZJ4MK5CXxTvIKmJyDb-AznTp7wAAAAHlOtF5AA")
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
