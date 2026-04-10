# ================== LOCK SYSTEM (FINAL STABLE) ==================

import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient
from pyrogram.enums import ButtonStyle
from EsproMusic import app
from config import MONGO_DB_URI

# ================== MONGO ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
locks_db = db["locks"]

PAGE_SIZE = 9

# ================== LOCK DATA ==================
LOCKS = {
    "ᴘʜᴏᴛᴏ": "ʙʟᴏᴄᴋs ᴀʟʟ ᴘʜᴏᴛᴏs",
    "ᴠɪᴅᴇᴏ": "ʙʟᴏᴄᴋs ᴀʟʟ ᴠɪᴅᴇᴏs",
    "ᴀᴜᴅɪᴏ": "ʙʟᴏᴄᴋs ᴀᴜᴅɪᴏ",
    "ᴅᴏᴄᴜᴍᴇɴᴛ": "ʙʟᴏᴄᴋs ғɪʟᴇs",
    "ᴜʀʟ": "ʙʟᴏᴄᴋs ʟɪɴᴋs",
    "ғᴏʀᴡᴀʀᴅ": "ɴᴏ ғᴏʀᴡᴀʀᴅs",
    "ɪɴʟɪɴᴇ": "ʙʟᴏᴄᴋs ɪɴʟɪɴᴇ ʙᴏᴛs",
    "ʙᴜᴛᴛᴏɴ": "ʙʟᴏᴄᴋs ʙᴜᴛᴛᴏɴs",
    "ɢɪғ": "ʙʟᴏᴄᴋs ɢɪғs"
}

LOCK_LIST = list(LOCKS.keys())

# ================== ADMIN ==================
async def is_admin(client, message: Message):
    try:
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

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

def unlock_all(chat_id):
    locks_db.delete_one({"chat_id": chat_id})

# ================== UI ==================
def format_status(lock, enabled):
    return f"🟢 {lock}" if enabled else f"🔴 {lock}"

def build_panel(chat_id, page=0):
    locks = get_locks(chat_id)

    start = page * PAGE_SIZE
    end = start + PAGE_SIZE
    items = LOCK_LIST[start:end]

    buttons, row = [], []

    for i, lock in enumerate(items, 1):
        row.append(
            InlineKeyboardButton(
                format_status(lock, lock in locks),
                callback_data=f"view_{lock}_{page}",
                style=ButtonStyle.PRIMARY
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

    buttons.append([InlineKeyboardButton("🚫 ᴜɴʟᴏᴄᴋ ᴀʟʟ", callback_data="unlock_all", style=ButtonStyle.SUCCESS)])

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
@app.on_message(filters.command(["lock", "locktypes"]) & filters.group)
async def lock_panel(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("admins only")

    await message.reply(
        main_text(),
        reply_markup=build_panel(message.chat.id, 0)
    )

# ================== UNLOCK ALL ==================
@app.on_message(filters.command("unlockall") & filters.group)
async def unlockall_cmd(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("admins only")

    unlock_all(message.chat.id)
    await message.reply("ᴀʟʟ ʀᴇsᴛʀɪᴄᴛɪᴏɴs ʀᴇᴍᴏᴠᴇᴅ .. ᴜsᴇʀs ᴀʀᴇ ғʀᴇᴇ ʀᴏɢᴇʀ🌷")

# ================== CALLBACK ==================
@app.on_callback_query()
async def callbacks(client, query):
    fake_msg = Message(
        id=0,
        date=None,
        chat=query.message.chat,
        from_user=query.from_user
    )

    if not await is_admin(client, fake_msg):
        return await query.answer("admins only", show_alert=True)

    data = query.data
    chat_id = query.message.chat.id

    if data == "unlock_all":
        unlock_all(chat_id)
        await query.message.edit_text(
            "all locks removed",
            reply_markup=build_panel(chat_id, 0)
        )

    elif data.startswith("page_"):
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
                [
                    InlineKeyboardButton(
                        "ᴛᴏɢɢʟᴇ ᴏɴ|ᴏғғ",
                        callback_data=f"toggle_{lock}_{page}",
                        style=ButtonStyle.PRIMARY
                    ),
                    InlineKeyboardButton(
                        "💗 ʙᴀᴄᴋ",
                        callback_data=f"page_{page}",
                        style=ButtonStyle.SECCUSS
                    )
                ]
          ])
        
 
    elif data.startswith("toggle_"):
        _, lock, page = data.split("_")
        status = toggle_lock(chat_id, lock)

        await query.message.edit_text(
            detail_text(lock, status),
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("Tᴏɢɢʟᴇ ᴏɴ|ᴏғғ", callback_data=f"toggle_{lock}_{page}", style=ButtonStyle.PRIMARY)],
                [InlineKeyboardButton("💗ʙᴀᴄᴋ", callback_data=f"page_{page}", style=ButtonStyle.SCCESS)]
            ])
        )

    await query.answer()

# ================== ENFORCER ==================
@app.on_message(filters.group)
async def enforce(client, message: Message):
    locks = get_locks(message.chat.id)

    if await is_admin(client, message):
        return

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
