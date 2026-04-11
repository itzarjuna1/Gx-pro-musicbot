# ================== PURGE SYSTEM (ROSE STYLE FINAL) ==================

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== DB ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
purge_db = db["purge"]

# ================== ADMIN CHECK ==================
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False


# ================== DELETE RANGE ==================
async def delete_range(client, chat_id, start, end):
    for msg_id in range(start, end + 1):
        try:
            await client.delete_messages(chat_id, msg_id)
        except:
            pass


# ================== PURGE ==================
@app.on_message(filters.command("purge") & filters.group)
async def purge(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ")

    start = message.reply_to_message.id
    end = message.id

    args = message.command

    # /purge 10
    if len(args) > 1:
        try:
            count = int(args[1])
            end = start + count
        except:
            return await message.reply("❌ ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ")

    await delete_range(client, message.chat.id, start, end)

    await message.reply("✅ ᴘᴜʀɢᴇᴅ")


# ================== SILENT PURGE ==================
@app.on_message(filters.command("spurge") & filters.group)
async def spurge(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        return

    start = message.reply_to_message.id
    end = message.id

    await delete_range(client, message.chat.id, start, end)

    try:
        await message.delete()
    except:
        pass


# ================== DELETE SINGLE ==================
@app.on_message(filters.command("del") & filters.group)
async def delete_msg(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴍᴇssᴀɢᴇ")

    try:
        await message.reply_to_message.delete()
        await message.delete()
    except:
        await message.reply("❌ ғᴀɪʟᴇᴅ")


# ================== PURGE FROM ==================
@app.on_message(filters.command("purgefrom") & filters.group)
async def purgefrom(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ")

    purge_db.update_one(
        {"chat_id": message.chat.id},
        {"$set": {"from": message.reply_to_message.id}},
        upsert=True
    )

    await message.reply("✅ sᴛᴀʀᴛ ᴘᴏɪɴᴛ sᴇᴛ")


# ================== PURGE TO ==================
@app.on_message(filters.command("purgeto") & filters.group)
async def purgeto(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("⚠️ ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ")

    data = purge_db.find_one({"chat_id": message.chat.id})

    if not data or "from" not in data:
        return await message.reply("❌ ᴜsᴇ /purgefrom ғɪʀsᴛ")

    start = data["from"]
    end = message.reply_to_message.id

    await delete_range(client, message.chat.id, start, end)

    purge_db.delete_one({"chat_id": message.chat.id})

    await message.reply("✅ ᴘᴜʀɢᴇᴅ")
