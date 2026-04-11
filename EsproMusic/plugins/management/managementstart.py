# ================== MANAGEMENT START PANEL ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from EsproMusic import app
import yaml

# ================== CONFIG ==================
SUPPORT_GROUP = "https://t.me/theinfinity_support"
SUPPORT_CHANNEL = "https://t.me/theinfinitynetwork"

VIDEO_URL = "https://files.catbox.moe/2y26pq.mp4"

# ================== LOAD STRINGS ==================
with open("strings/langs/en.yml", "r", encoding="utf-8") as f:
    STRINGS = yaml.safe_load(f)

def get_string(key):
    return STRINGS.get(key, "text not found")

# ================== BUTTONS ==================
def mstart_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP),
                InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=SUPPORT_CHANNEL),
            ],
            [
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_mstart")
            ]
        ]
    )

# ================== COMMAND ==================
@app.on_message(filters.command("mstart") & filters.group)
async def mstart(client, message: Message):
    text = get_string("mstart_1")

    await message.reply_video(
        video=VIDEO_URL,
        caption=text,
        reply_markup=mstart_buttons(),
    )

# ================== CALLBACK ==================
@app.on_callback_query(filters.regex("close_mstart"))
async def close_panel(client, query):
    await query.message.delete()
