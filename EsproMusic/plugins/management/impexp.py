import json
import time
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]

COLLECTIONS = {
    "locks": db["locks"],
    "filters": db["filters"],
    "notes": db["notes"],
    "warns": db["warns"],
    "rules": db["rules"],
    "greetings": db["greetings"],
    "pins": db["pins"],
}

LAST_USED = {}

def rate_limit(chat_id):
    now = time.time()
    if chat_id in LAST_USED and now - LAST_USED[chat_id] < 10:
        return False
    LAST_USED[chat_id] = now
    return True

async def is_admin(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]

async def is_owner(client, chat_id, user_id):
    member = await client.get_chat_member(chat_id, user_id)
    return member.status == ChatMemberStatus.OWNER

@app.on_message(filters.command("export") & filters.group)
async def export_data(client, message: Message):

    chat_id = message.chat.id

    if not await is_admin(client, chat_id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴ ᴏɴʟʏ")

    if not rate_limit(chat_id):
        return await message.reply("⏳ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ")

    args = message.command[1:]

    export_data = {}

    modules = args if args else COLLECTIONS.keys()

    for module in modules:
        if module in COLLECTIONS:
            data = list(COLLECTIONS[module].find({"chat_id": chat_id}, {"_id": 0}))
            export_data[module] = data

    file_name = f"backup_{chat_id}.json"

    with open(file_name, "w") as f:
        json.dump(export_data, f, indent=4)

    await message.reply_document(
        file_name,
        caption="📦 ᴄʜᴀᴛ ᴇxᴘᴏʀᴛ ʀᴇᴀᴅʏ"
    )

@app.on_message(filters.command("import") & filters.group)
async def import_data(client, message: Message):

    chat_id = message.chat.id

    if not await is_owner(client, chat_id, message.from_user.id):
        return await message.reply("👑 ᴏᴡɴᴇʀ ᴏɴʟʏ")

    if not message.reply_to_message or not message.reply_to_message.document:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴊsᴏɴ ғɪʟᴇ")

    if not rate_limit(chat_id):
        return await message.reply("⏳ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ")

    file_path = await message.reply_to_message.download()

    with open(file_path, "r") as f:
        data = json.load(f)

    args = message.command[1:]
    modules = args if args else data.keys()

    for module in modules:
        if module in COLLECTIONS and module in data:

            # remove old data
            COLLECTIONS[module].delete_many({"chat_id": chat_id})

            # insert new
            for item in data[module]:
                item["chat_id"] = chat_id
                COLLECTIONS[module].insert_one(item)

    await message.reply("✅ ɪᴍᴘᴏʀᴛ ᴄᴏᴍᴘʟᴇᴛᴇ")

@app.on_message(filters.command("reset") & filters.group)
async def reset_chat(client, message: Message):

    chat_id = message.chat.id

    if not await is_owner(client, chat_id, message.from_user.id):
        return await message.reply("👑 ᴏᴡɴᴇʀ ᴏɴʟʏ")

    if not rate_limit(chat_id):
        return await message.reply("⏳ ᴛʀʏ ᴀɢᴀɪɴ ʟᴀᴛᴇʀ")

    for collection in COLLECTIONS.values():
        collection.delete_many({"chat_id": chat_id})

    await message.reply("🗑 ᴄʜᴀᴛ ʀᴇsᴇᴛ ᴄᴏᴍᴘʟᴇᴛᴇ")
