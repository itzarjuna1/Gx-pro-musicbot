# ================== MANAGEMENT START PANEL ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ButtonStyle
from EsproMusic import app
from EsproMusic.utils.language import get_string

# ===== LINKS =====
SUPPORT_GROUP = "https://t.me/theinfinity_support"
SUPPORT_CHANNEL = "https://t.me/theinfinitynetwork"

# ================== BUTTONS ==================
def mstart_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP, style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=SUPPORT_CHANNEL, style=ButtonStyle.PRIMARY),
            ],
            [
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_mstart", style=ButtonStyle.DANGER)
            ]
        ]
    )

# ================== COMMAND ==================
@app.on_message(filters.command("mstart") & filters.group)
async def mstart(client, message: Message):
    text = get_string(message.chat.id, "mstart_1")

    await message.reply(
        text,
        reply_markup=mstart_buttons()
    )

# ================== CALLBACK ==================
@app.on_callback_query(filters.regex("close_mstart"))
async def close_panel(client, query):
    await query.message.delete()
