# ================== MANAGEMENT START PANEL ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ParseMode, ButtonStyle

from EsproMusic import app

# ===== LINKS =====
SUPPORT_GROUP = "https://t.me/theinfinity_support"
SUPPORT_CHANNEL = "https://t.me/theinfinitynetwork"

# ================== TEXT ==================
def mstart_text():
    return (
        "╭─〔 ⚙️ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ ᴍᴏᴅᴇ 〕─╮\n"
        "│\n"
        "│ ✦ ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴀᴅᴠᴀɴᴄᴇᴅ ᴄʜᴀᴛ ᴄᴏɴᴛʀᴏʟ\n"
        "│\n"
        "│ ᴛʜɪs ᴍᴏᴅᴇ ᴀʟʟᴏᴡs ʏᴏᴜ ᴛᴏ ғᴜʟʟʏ\n"
        "│ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ ᴡɪᴛʜ ᴘᴏᴡᴇʀғᴜʟ\n"
        "│ ᴛᴏᴏʟs ᴀɴᴅ ᴀᴜᴛᴏᴍᴀᴛɪᴏɴ sʏsᴛᴇᴍs.\n"
        "│\n"
        "│ ✧ ʟᴏᴄᴋ & ᴍᴇᴅɪᴀ ᴄᴏɴᴛʀᴏʟs\n"
        "│ ✧ ʙᴀɴ / ᴍᴜᴛᴇ / ᴀᴅᴍɪɴ ᴛᴏᴏʟs\n"
        "│ ✧ ғɪʟᴛᴇʀs & ᴀᴜᴛᴏ ʀᴇᴘʟɪᴇs\n"
        "│ ✧ ᴀɴᴛɪ sᴘᴀᴍ & sᴇᴄᴜʀɪᴛʏ\n"
        "│ ✧ ɪᴍᴘᴏʀᴛ / ᴇxᴘᴏʀᴛ sᴇᴛᴛɪɴɢs\n"
        "│\n"
        "│ ⚡ ᴇᴠᴇʀʏᴛʜɪɴɢ ɪɴ ᴏɴᴇ ᴘʟᴀᴄᴇ\n"
        '│ <a href="https://files.catbox.moe/2y26pq.mp4">ғᴏʀ sᴍᴀʀᴛ ɢʀᴏᴜᴘ ᴍᴀɴᴀɢᴇᴍᴇɴᴛ</a>\n'
        "│\n"
        "╰────────────────╯"
    )

# ================== BUTTONS ==================
def mstart_buttons():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💬 sᴜᴘᴘᴏʀᴛ", url=SUPPORT_GROUP, style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("📢 ᴄʜᴀɴɴᴇʟ", url=SUPPORT_CHANNEL, style=ButtonStyle.SUCCESS)
            ],
            [
                InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="close_mstart", style=ButtonStyle.DANGER)
            ]
        ]
    )

# ================== COMMAND ==================
@app.on_message(filters.command("mstart") & filters.group)
async def mstart(client, message: Message):
    await message.reply(
        mstart_text(),
        reply_markup=mstart_buttons(),
        parse_mode="html"   # IMPORTANT
    )

# ================== CALLBACK ==================
@app.on_callback_query(filters.regex("close_mstart"))
async def close_panel(client, query):
    await query.message.delete()
