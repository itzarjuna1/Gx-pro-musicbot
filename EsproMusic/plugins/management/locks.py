# ================== ULTRA LOCK SYSTEM (ESPRO MUSIC COMPATIBLE) ==================

import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pymongo import MongoClient

from EsproMusic import app
from EsproMusic.utils.filters import command
from config import MONGO_DB_URI

# ================== MONGO ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
locks_db = db["locks"]

PAGE_SIZE = 9

# ================== LOCK DATA ==================
LOCKS = {
    "photo": "ʙʟᴏᴄᴋs ᴀʟʟ ᴘʜᴏᴛᴏs",
    "video": "ʙʟᴏᴄᴋs ᴀʟʟ ᴠɪᴅᴇᴏs",
    "audio": "ʙʟᴏᴄᴋs ᴀᴜᴅɪᴏ",
    "document": "ʙʟᴏᴄᴋs ғɪʟᴇs",
    "url": "ʙʟᴏᴄᴋs ʟɪɴᴋs",
    "forward": "ɴᴏ ғᴏʀᴡᴀʀᴅs",
    "inline": "ʙʟᴏᴄᴋs ɪɴʟɪɴᴇ ʙᴏᴛs",
    "button": "ʙʟᴏᴄᴋs ʙᴜᴛᴛᴏɴs",
    "gif": "ʙʟᴏᴄᴋs ɢɪғs"
}

LOCK_LIST = list(LOCKS.keys())

# ================== DB ==================
def get_locks(chat_id):
    data = locks_db.find_one({"chat_id": chat_id})
    return data["locks"] if data else []

def toggle_lock(chat_id, lock):
    locks = get_locks(chat_id)

    if lock in locks:
        locks_db.update_one({"chat_id": chat_id}, {"$pull": {"locks": lock}})
        return False
    else:
        locks_db.update_one(
            {"chat_id": chat_id},
            {"$addToSet": {"locks": lock}},
            upsert=True
        )
        return True

# ================== UI ==================
def format_status(lock, enabled):
    return f"🟢 {lock}" if enabled else f"🔴 {lock}"

def build_panel(chat_id, page=0):
    locks = get_locks(chat_id)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    items = LOCK_LIST[start:end]

    buttons = []
    row = []

    for i, lock in enumerate(items, 1):
        row.append(
            InlineKeyboardButton(
                format_status(lock, lock in locks),
                callback_data=f"view_{lock}_{page}"
            )
        )
        if i % 3 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⏮ ʙᴀᴄᴋ", callback_data=f"page_{page-1}"))
    if end < len(LOCK_LIST):
        nav.append(InlineKeyboardButton("ɴᴇxᴛ ⏭", callback_data=f"page_{page+1}"))

    if nav:
        buttons.append(nav)

    return InlineKeyboardMarkup(buttons)

# ================== TEXT ==================
def main_text():
    return (
        "╭─〔 🔐 ʟᴏᴄᴋ ᴘᴀɴᴇʟ 〕─╮\n"
        "│ ᴛᴀᴘ ᴀ ʟᴏᴄᴋ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ\n"
        "╰────────────────╯"
    )

def detail_text(lock, enabled):
    state = "🟢 ᴇɴᴀʙʟᴇᴅ" if enabled else "🔴 ᴅɪsᴀʙʟᴇᴅ"
    return (
        f"╭─〔 ⚙️ {lock} 〕─╮\n"
        f"│ {LOCKS[lock]}\n"
        f"│ sᴛᴀᴛᴜs: {state}\n"
        f"╰────────────────╯"
    )

# ================== COMMAND ==================
@app.on_message(command(["locktypes", "locks"]) & filters.group)
async def locktypes(_, message):
    await message.reply_text(
        main_text(),
        reply_markup=build_panel(message.chat.id, 0)
    )

# ================== CALLBACK ==================
@app.on_callback_query()
async def callbacks(_, query):
    data = query.data
    chat_id = query.message.chat.id

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        await query.message.edit_text(
            main_text(),
            reply_markup=build_panel(chat_id, page)
        )

    elif data.startswith("view_"):
        _, lock, page = data.split("_")
        locks = get_locks(chat_id)

        await query.message.edit_text(
            detail_text(lock, lock in locks),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{lock}_{page}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"page_{page}")]
            ])
        )

    elif data.startswith("toggle_"):
        _, lock, page = data.split("_")
        status = toggle_lock(chat_id, lock)

        await query.message.edit_text(
            detail_text(lock, status),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{lock}_{page}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"page_{page}")]
            ])
        )

    await query.answer()

# ================== ENFORCER ==================
@app.on_message(filters.group)
async def enforce(_, message):
    locks = get_locks(message.chat.id)

    try:
        if "photo" in locks and message.photo:
            await message.delete()

        elif "video" in locks and message.video:
            await message.delete()

        elif "audio" in locks and message.audio:
            await message.delete()

        elif "document" in locks and message.document:
            await message.delete()

        elif "gif" in locks and message.animation:
            await message.delete()

        elif "forward" in locks and message.forward_date:
            await message.delete()

        elif "inline" in locks and message.via_bot:
            await message.delete()

        elif "button" in locks and message.reply_markup:
            await message.delete()

        elif "url" in locks:
            text = message.text or message.caption or ""
            if re.search(r"(https?://|www\.)", text):
                await message.delete()

    except:
        pass
