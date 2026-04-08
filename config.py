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

BOT_NAME = "🫧 ʙᴀᴋᴀ ×͜࿐"
REVIVE_COST = 500
PROTECT_1D_COST = 1000
PROTECT_2D_COST = 1800
REGISTER_BONUS = 5000
CLAIM_BONUS = 2000
RIDDLE_REWARD = 1000
DIVORCE_COST = 2000
WAIFU_PROPOSE_COST = 5000
TAX_RATE = 0.10
MARRIED_TAX_RATE = 0.05
AUTO_REVIVE_HOURS = 6
AUTO_REVIVE_BONUS = 200
ITEM_EXPIRY_HOURS = 24 
MIN_CLAIM_MEMBERS = 100

# --- 🛒 BALANCED SHOP ITEMS (Max 60%) ---
SHOP_ITEMS = [
    # WEAPONS (Damage Buff - Increases Kill Reward)
    {"id": "stick", "name": "🪵 Stick", "price": 500, "type": "weapon", "buff": 0.01},
    {"id": "brick", "name": "🧱 Brick", "price": 1000, "type": "weapon", "buff": 0.02},
    {"id": "slingshot", "name": "🪃 Slingshot", "price": 2000, "type": "weapon", "buff": 0.03},
    {"id": "knife", "name": "🔪 Knife", "price": 3500, "type": "weapon", "buff": 0.05},
    {"id": "bat", "name": "🏏 Bat", "price": 5000, "type": "weapon", "buff": 0.08},
    {"id": "axe", "name": "🪓 Axe", "price": 7500, "type": "weapon", "buff": 0.10},
    {"id": "hammer", "name": "🔨 Hammer", "price": 10000, "type": "weapon", "buff": 0.12},
    {"id": "chainsaw", "name": "🪚 Chainsaw", "price": 15000, "type": "weapon", "buff": 0.15},
    {"id": "pistol", "name": "🔫 Pistol", "price": 25000, "type": "weapon", "buff": 0.20},
    {"id": "shotgun", "name": "🧨 Shotgun", "price": 40000, "type": "weapon", "buff": 0.25},
    {"id": "uzi", "name": "🔫 Uzi", "price": 55000, "type": "weapon", "buff": 0.30},
    {"id": "katana", "name": "⚔️ Katana", "price": 75000, "type": "weapon", "buff": 0.35},
    {"id": "ak47", "name": "💥 AK-47", "price": 100000, "type": "weapon", "buff": 0.40},
    {"id": "minigun", "name": "🔥 Minigun", "price": 150000, "type": "weapon", "buff": 0.45},
    {"id": "sniper", "name": "🎯 Sniper", "price": 200000, "type": "weapon", "buff": 0.50},
    {"id": "rpg", "name": "🚀 RPG", "price": 300000, "type": "weapon", "buff": 0.55},
    {"id": "tank", "name": "🚜 Tank", "price": 500000, "type": "weapon", "buff": 0.58},
    {"id": "laser", "name": "⚡ Laser", "price": 800000, "type": "weapon", "buff": 0.59},
    {"id": "deathnote", "name": "📓 Death Note", "price": 5000000, "type": "weapon", "buff": 0.60}, # Max Dmg

    # ARMOR (Block Chance - Stops Robberies)
    {"id": "paper", "name": "📰 Newspaper", "price": 500, "type": "armor", "buff": 0.01},
    {"id": "cardboard", "name": "📦 Cardboard", "price": 1000, "type": "armor", "buff": 0.02},
    {"id": "cloth", "name": "👕 Cloth", "price": 2500, "type": "armor", "buff": 0.05},
    {"id": "leather", "name": "🧥 Leather", "price": 8000, "type": "armor", "buff": 0.08},
    {"id": "chain", "name": "⛓️ Chain", "price": 20000, "type": "armor", "buff": 0.10},
    {"id": "riot", "name": "🛡️ Riot Shield", "price": 40000, "type": "armor", "buff": 0.15},
    {"id": "swat", "name": "👮 SWAT", "price": 60000, "type": "armor", "buff": 0.20},
    {"id": "iron", "name": "🦾 Iron Suit", "price": 100000, "type": "armor", "buff": 0.25},
    {"id": "diamond", "name": "💎 Diamond", "price": 200000, "type": "armor", "buff": 0.30},
    {"id": "obsidian", "name": "⚫ Obsidian", "price": 400000, "type": "armor", "buff": 0.35},
    {"id": "nano", "name": "🧬 Nano Suit", "price": 700000, "type": "armor", "buff": 0.40},
    {"id": "vibranium", "name": "🛡️ Vibranium", "price": 1500000, "type": "armor", "buff": 0.50},
    {"id": "force", "name": "🔮 Forcefield", "price": 3000000, "type": "armor", "buff": 0.55},
    {"id": "plot", "name": "🎬 Plot Armor", "price": 10000000, "type": "armor", "buff": 0.60}, # Max Block

    # FLEX (Safe Assets - Burn on Death)
    {"id": "cookie", "name": "🍪 Cookie", "price": 100, "type": "flex", "buff": 0},
    {"id": "coffee", "name": "☕ Starbucks", "price": 300, "type": "flex", "buff": 0},
    {"id": "rose", "name": "🌹 Rose", "price": 500, "type": "flex", "buff": 0},
    {"id": "sushi", "name": "🍣 Sushi Platter", "price": 2000, "type": "flex", "buff": 0},
    {"id": "vodka", "name": "🍾 Vodka", "price": 5000, "type": "flex", "buff": 0},
    {"id": "ring", "name": "💍 Gold Ring", "price": 10000, "type": "flex", "buff": 0},
    {"id": "ps5", "name": "🎮 PS5 Pro", "price": 15000, "type": "flex", "buff": 0},
    {"id": "iphone", "name": "📱 iPhone 16 Pro", "price": 25000, "type": "flex", "buff": 0},
    {"id": "macbook", "name": "💻 MacBook M3", "price": 50000, "type": "flex", "buff": 0},
    {"id": "gucci", "name": "👜 Gucci Bag", "price": 75000, "type": "flex", "buff": 0},
    {"id": "rolex", "name": "⌚ Rolex", "price": 100000, "type": "flex", "buff": 0},
    {"id": "diamond_ring", "name": "💎 Solitaire", "price": 250000, "type": "flex", "buff": 0},
    {"id": "tesla", "name": "🚗 Tesla", "price": 400000, "type": "flex", "buff": 0},
    {"id": "lambo", "name": "🏎️ Lambo", "price": 800000, "type": "flex", "buff": 0},
    {"id": "heli", "name": "🚁 Helicopter", "price": 1500000, "type": "flex", "buff": 0},
    {"id": "yacht", "name": "🛳️ Super Yacht", "price": 3000000, "type": "flex", "buff": 0},
    {"id": "mansion", "name": "🏰 Mansion", "price": 5000000, "type": "flex", "buff": 0},
    {"id": "jet", "name": "✈️ Private Jet", "price": 10000000, "type": "flex", "buff": 0},
    {"id": "island", "name": "🏝️ Private Island", "price": 50000000, "type": "flex", "buff": 0},
    {"id": "moon", "name": "🌑 The Moon", "price": 100000000, "type": "flex", "buff": 0},
    {"id": "mars", "name": "🪐 Mars", "price": 500000000, "type": "flex", "buff": 0},
    {"id": "sun", "name": "☀️ The Sun", "price": 1000000000, "type": "flex", "buff": 0},
    {"id": "galaxy", "name": "🌌 Milky Way", "price": 5000000000, "type": "flex", "buff": 0},
    {"id": "blackhole", "name": "🕳️ Black Hole", "price": 9999999999, "type": "flex", "buff": 0},
]

HEROKU_APP_NAME = getenv("HEROKU_APP_NAME")
HEROKU_API_KEY = getenv("HEROKU_API_KEY")

UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/itzarjuna1/Gx-pro-musicbot")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "master")
GIT_TOKEN = getenv("GIT_TOKEN", None)

SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/theinfinitynetwork")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/theinfinity_suppport")

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

client = AsyncIOMotorClient(MONGO_DB_URI)
db = client['Character_catcher']
collection = db['anime_characters_lol']
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totalsssssss']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']

START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/62lp2j.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/62lp2j.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
STATS_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/62lp2j.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/62lp2j.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/62lp2j.jpg"

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
