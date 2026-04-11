# ================== FILTER SYSTEM ==================

import re
from pyrogram import filters
from pyrogram.types import Message
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI


# ================== DB ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
filters_db = db["filters"]


# ================== DB FUNCS ==================
def add_filter(chat_id, trigger, reply):
    filters_db.update_one(
        {"chat_id": chat_id, "trigger": trigger},
        {"$set": {"reply": reply}},
        upsert=True
    )


def remove_filter(chat_id, trigger):
    filters_db.delete_one({"chat_id": chat_id, "trigger": trigger})


def get_filters(chat_id):
    return list(filters_db.find({"chat_id": chat_id}))


def remove_all(chat_id):
    filters_db.delete_many({"chat_id": chat_id})


# ================== ADMIN CHECK ==================
async def is_admin(client, message: Message):
    try:
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in ("administrator", "creator")
    except:
        return False


# ================== ADD FILTER ==================
@app.on_message(filters.command("filter") & filters.group)
async def addfilter(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 3:
        return await message.reply_text(
            "ᴜsᴀɢᴇ:\n/filter <ᴛʀɪɢɢᴇʀ> <ʀᴇᴘʟʏ>"
        )

    trigger = message.command[1].lower()
    reply = message.text.split(None, 2)[2]

    add_filter(message.chat.id, trigger, reply)

    await message.reply_text(f"✅ ғɪʟᴛᴇʀ ᴀᴅᴅᴇᴅ: `{trigger}`")


# ================== LIST FILTERS ==================
@app.on_message(filters.command("filters") & filters.group)
async def listfilters(client, message: Message):

    data = get_filters(message.chat.id)

    if not data:
        return await message.reply_text("ɴᴏ ғɪʟᴛᴇʀs sᴇᴛ.")

    text = "╭─〔 🧠 ғɪʟᴛᴇʀs 〕─╮\n│\n"

    for f in data:
        text += f"│ • `{f['trigger']}`\n"

    text += "│\n╰──────────────╯"

    await message.reply_text(text)


# ================== REMOVE FILTER ==================
@app.on_message(filters.command("stop") & filters.group)
async def stopfilter(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply_text("ɢɪᴠᴇ ᴀ ᴛʀɪɢɢᴇʀ.")

    trigger = message.command[1].lower()

    remove_filter(message.chat.id, trigger)

    await message.reply_text(f"❌ ғɪʟᴛᴇʀ ʀᴇᴍᴏᴠᴇᴅ: `{trigger}`")


# ================== REMOVE ALL ==================
@app.on_message(filters.command("stopall") & filters.group)
async def stopall(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    remove_all(message.chat.id)

    await message.reply_text("🚫 ᴀʟʟ ғɪʟᴛᴇʀs ʀᴇᴍᴏᴠᴇᴅ")


# ================== FILTER REPLY ==================
@app.on_message(filters.text & filters.group, group=2)
async def filter_reply(client, message: Message):

    if not message.text:
        return

    text = message.text.lower()
    data = get_filters(message.chat.id)

    for f in data:
        trigger = f["trigger"]

        # exact word match OR phrase match
        if re.search(rf"\b{re.escape(trigger)}\b", text):
            try:
                await message.reply_text(f["reply"])
            except:
                pass
            break
