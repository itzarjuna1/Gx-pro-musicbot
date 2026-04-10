# ================== ULTRA AESTHETIC LOCK SYSTEM ==================

import re
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler, CallbackQueryHandler,
    MessageHandler, Filters, CallbackContext
)
from pymongo import MongoClient

# ✅ IMPORT FROM CONFIG
from config import MONGO_DB_URI

# ================== CONFIG ==================
PAGE_SIZE = 9

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
locks_db = db["locks"]

# ================== LOCK DATA ==================
LOCKS = {
    "photo": "ʙʟᴏᴄᴋs ᴀʟʟ ᴘʜᴏᴛᴏs",
    "video": "ʙʟᴏᴄᴋs ᴀʟʟ ᴠɪᴅᴇᴏs",
    "audio": "ʙʟᴏᴄᴋs ᴀʟʟ ᴀᴜᴅɪᴏ",
    "document": "ʙʟᴏᴄᴋs ғɪʟᴇs",
    "url": "ʙʟᴏᴄᴋs ᴀʟʟ ʟɪɴᴋs",
    "forward": "ᴘʀᴇᴠᴇɴᴛs ғᴏʀᴡᴀʀᴅs",
    "inline": "ʙʟᴏᴄᴋs ɪɴʟɪɴᴇ ʙᴏᴛs",
    "button": "ʀᴇᴍᴏᴠᴇs ʙᴜᴛᴛᴏɴ ᴍᴇssᴀɢᴇs",
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
        "╭─〔 🔐 ʟᴏᴄᴋ ᴄᴏɴᴛʀᴏʟ ᴘᴀɴᴇʟ 〕─╮\n"
        "│\n"
        "│ ᴛᴀᴘ ᴀ ʟᴏᴄᴋ ᴛᴏ ᴄᴏɴғɪɢᴜʀᴇ\n"
        "│ ᴍᴀɴᴀɢᴇ ʏᴏᴜʀ ɢʀᴏᴜᴘ sᴇᴄᴜʀɪᴛʏ\n"
        "│\n"
        "╰────────────────────╯"
    )

def detail_text(lock, enabled):
    state = "🟢 ᴇɴᴀʙʟᴇᴅ" if enabled else "🔴 ᴅɪsᴀʙʟᴇᴅ"
    return (
        f"╭─〔 ⚙️ {lock} 〕─╮\n"
        f"│\n"
        f"│ 📖 {LOCKS[lock]}\n"
        f"│\n"
        f"│ sᴛᴀᴛᴜs : {state}\n"
        f"│\n"
        f"╰────────────────╯"
    )

# ================== COMMAND ==================
def locktypes(update: Update, context: CallbackContext):
    update.message.reply_text(
        main_text(),
        reply_markup=build_panel(update.effective_chat.id, 0)
    )

# ================== CALLBACK ==================
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()

    data = query.data
    chat_id = query.message.chat.id

    if data.startswith("page_"):
        page = int(data.split("_")[1])
        query.edit_message_text(
            main_text(),
            reply_markup=build_panel(chat_id, page)
        )

    elif data.startswith("view_"):
        _, lock, page = data.split("_")
        locks = get_locks(chat_id)

        query.edit_message_text(
            detail_text(lock, lock in locks),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{lock}_{page}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"page_{page}")]
            ])
        )

    elif data.startswith("toggle_"):
        _, lock, page = data.split("_")
        status = toggle_lock(chat_id, lock)

        query.edit_message_text(
            detail_text(lock, status),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔁 ᴛᴏɢɢʟᴇ", callback_data=f"toggle_{lock}_{page}")],
                [InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data=f"page_{page}")]
            ])
        )

# ================== ENFORCER ==================
def enforce(update: Update, context: CallbackContext):
    msg = update.effective_message
    chat_id = update.effective_chat.id
    locks = get_locks(chat_id)

    try:
        if "photo" in locks and msg.photo:
            msg.delete()

        elif "video" in locks and msg.video:
            msg.delete()

        elif "audio" in locks and msg.audio:
            msg.delete()

        elif "document" in locks and msg.document:
            msg.delete()

        elif "gif" in locks and msg.animation:
            msg.delete()

        elif "forward" in locks and msg.forward_date:
            msg.delete()

        elif "inline" in locks and msg.via_bot:
            msg.delete()

        elif "button" in locks and msg.reply_markup:
            msg.delete()

        elif "url" in locks:
            text = msg.text or msg.caption or ""
            if re.search(r"(https?://|www\.)", text):
                msg.delete()

    except:
        pass

# ================== SETUP ==================
def setup(dispatcher):
    dispatcher.add_handler(CommandHandler("locktypes", locktypes))
    dispatcher.add_handler(CallbackQueryHandler(button_handler))
    dispatcher.add_handler(MessageHandler(Filters.all, enforce))
