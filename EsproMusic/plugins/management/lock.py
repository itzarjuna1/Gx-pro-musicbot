

import re
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
locks_db = db["locks"]

PAGE_SIZE = 6

LOCKS = {
    "all": "ʟᴏᴄᴋ ᴇᴠᴇʀʏᴛʜɪɴɢ",
    "album": "ʙʟᴏᴄᴋ ᴀʟʙᴜᴍs",
    "anonchannel": "ʙʟᴏᴄᴋ ᴀɴᴏɴ ᴘᴏsᴛs",
    "audio": "ʙʟᴏᴄᴋ ᴀᴜᴅɪᴏ",
    "bot": "ʙʟᴏᴄᴋ ʙᴏᴛs",
    "botlink": "ʙʟᴏᴄᴋ ʙᴏᴛ ʟɪɴᴋs",
    "button": "ʙʟᴏᴄᴋ ʙᴜᴛᴛᴏɴs",
    "cashtag": "ʙʟᴏᴄᴋ $ᴛᴀɢs",
    "checklist": "ʙʟᴏᴄᴋ ᴄʜᴇᴄᴋʟɪsᴛ",
    "cjk": "ʙʟᴏᴄᴋ ᴄᴊᴋ ᴛᴇxᴛ",
    "command": "ʙʟᴏᴄᴋ /ᴄᴏᴍᴍᴀɴᴅs",
    "comment": "ʙʟᴏᴄᴋ ᴄᴏᴍᴍᴇɴᴛs",
    "contact": "ʙʟᴏᴄᴋ ᴄᴏɴᴛᴀᴄᴛs",
    "cyrillic": "ʙʟᴏᴄᴋ ᴄʏʀɪʟʟɪᴄ",
    "document": "ʙʟᴏᴄᴋ ғɪʟᴇs",
    "email": "ʙʟᴏᴄᴋ ᴇᴍᴀɪʟs",
    "emoji": "ʙʟᴏᴄᴋ ᴇᴍᴏᴊɪ",
    "emojicustom": "ʙʟᴏᴄᴋ ᴄᴜsᴛᴏᴍ ᴇᴍᴏᴊɪ",
    "emojigame": "ʙʟᴏᴄᴋ ᴇᴍᴏᴊɪ ɢᴀᴍᴇs",
    "emojionly": "ᴏɴʟʏ ᴇᴍᴏᴊɪ",
    "externalreply": "ʙʟᴏᴄᴋ ᴇxᴛᴇʀɴᴀʟ ʀᴇᴘʟʏ",
    "forward": "ʙʟᴏᴄᴋ ғᴏʀᴡᴀʀᴅs",
    "forwardbot": "ʙʟᴏᴄᴋ ғᴏʀᴡᴀʀᴅ ʙᴏᴛ",
    "forwardchannel": "ʙʟᴏᴄᴋ ғᴏʀᴡᴀʀᴅ ᴄʜᴀɴɴᴇʟ",
    "forwardstory": "ʙʟᴏᴄᴋ ғᴏʀᴡᴀʀᴅ sᴛᴏʀʏ",
    "forwarduser": "ʙʟᴏᴄᴋ ғᴏʀᴡᴀʀᴅ ᴜsᴇʀ",
    "game": "ʙʟᴏᴄᴋ ɢᴀᴍᴇs",
    "gif": "ʙʟᴏᴄᴋ ɢɪғs",
    "inline": "ʙʟᴏᴄᴋ ɪɴʟɪɴᴇ ʙᴏᴛs",
    "invitelink": "ʙʟᴏᴄᴋ ɪɴᴠɪᴛᴇ ʟɪɴᴋs",
    "location": "ʙʟᴏᴄᴋ ʟᴏᴄᴀᴛɪᴏɴ",
    "phone": "ʙʟᴏᴄᴋ ᴘʜᴏɴᴇ",
    "photo": "ʙʟᴏᴄᴋ ᴘʜᴏᴛᴏs",
    "poll": "ʙʟᴏᴄᴋ ᴘᴏʟʟs",
    "rtl": "ʙʟᴏᴄᴋ ʀᴛʟ",
    "spoiler": "ʙʟᴏᴄᴋ sᴘᴏɪʟᴇʀs",
    "sticker": "ʙʟᴏᴄᴋ sᴛɪᴄᴋᴇʀs",
    "stickeranimated": "ʙʟᴏᴄᴋ ᴀɴɪᴍᴀᴛᴇᴅ",
    "stickerpremium": "ʙʟᴏᴄᴋ ᴘʀᴇᴍɪᴜᴍ",
    "text": "ʙʟᴏᴄᴋ ᴛᴇxᴛ",
    "url": "ʙʟᴏᴄᴋ ʟɪɴᴋs",
    "video": "ʙʟᴏᴄᴋ ᴠɪᴅᴇᴏs",
    "videonote": "ʙʟᴏᴄᴋ ᴠɪᴅᴇᴏ ɴᴏᴛᴇ",
    "voice": "ʙʟᴏᴄᴋ ᴠᴏɪᴄᴇ",
    "zalgо": "ʙʟᴏᴄᴋ ᴢᴀʟɢᴏ"
}

LOCK_LIST = list(LOCKS.keys())

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

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

def get_pattern_style(i):
    styles = [ButtonStyle.PRIMARY, ButtonStyle.SUCCESS, ButtonStyle.DANGER]
    return styles[i % 3]

def build_panel(chat_id, page=0):
    locks = get_locks(chat_id)
    start = page * PAGE_SIZE
    items = LOCK_LIST[start:start + PAGE_SIZE]

    buttons, row = [], []

    for i, lock in enumerate(items, 1):
        row.append(
            InlineKeyboardButton(
                f"{'🟢' if lock in locks else '🔴'} {lock}",
                callback_data=f"toggle_{lock}_{page}",
                style=get_pattern_style(i)
            )
        )
        if i % 2 == 0:
            buttons.append(row)
            row = []

    if row:
        buttons.append(row)

    if start + PAGE_SIZE < len(LOCK_LIST):
        buttons.append([
            InlineKeyboardButton("Next ⏭", callback_data=f"page_{page+1}", style=ButtonStyle.PRIMARY)
        ])

    buttons.append([
        InlineKeyboardButton("Unlock All", callback_data="unlock_all", style=ButtonStyle.SUCCESS)
    ])

    return InlineKeyboardMarkup(buttons
                                
@app.on_message(filters.command("lock") & filters.group)
async def lock_panel(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("Admins only")

    await message.reply("🔐 Lock Panel", reply_markup=build_panel(message.chat.id))


@app.on_callback_query()
async def callbacks(client, query):
    chat_id = query.message.chat.id

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("Admins only", show_alert=True)

    data = query.data

    if data == "unlock_all":
        unlock_all(chat_id)

    elif data.startswith("page_"):
        page = int(data.split("_")[1])
        return await query.message.edit_reply_markup(build_panel(chat_id, page))

    elif data.startswith("toggle_"):
        _, lock, page = data.split("_")
        toggle_lock(chat_id, lock)
        return await query.message.edit_reply_markup(build_panel(chat_id, int(page)))

    await query.answer()

@app.on_message(filters.group, group=1)
async def enforce(client, message: Message):

    if message.text and message.text.startswith("/"):
        return

    locks = get_locks(message.chat.id)

    if message.from_user and await is_admin(client, message.chat.id, message.from_user.id):
        return

    try:
        text = message.text or message.caption or ""

        if "all" in locks:
            return await message.delete()

        if "audio" in locks:
            if message.audio or message.voice:
                return await message.delete()
            if message.document and message.document.mime_type and "audio" in message.document.mime_type:
                return await message.delete()

        if "photo" in locks and message.photo:
            return await message.delete()

        if "video" in locks and message.video:
            return await message.delete()

        if "gif" in locks and message.animation:
            return await message.delete()

        if "document" in locks and message.document:
            return await message.delete()

        if "sticker" in locks and message.sticker:
            return await message.delete()

        if "videonote" in locks and message.video_note:
            return await message.delete()

        if "voice" in locks and message.voice:
            return await message.delete()

        if "contact" in locks and message.contact:
            return await message.delete()

        if "location" in locks and message.location:
            return await message.delete()

        if "poll" in locks and message.poll:
            return await message.delete()

        if "forward" in locks and message.forward_date:
            return await message.delete()

        if "inline" in locks and message.via_bot:
            return await message.delete()

        if "button" in locks and message.reply_markup:
            return await message.delete()

        if "url" in locks and re.search(r"(https?://|www\.)", text):
            return await message.delete()

        if "text" in locks and message.text:
            return await message.delete()

    except:
        pass
