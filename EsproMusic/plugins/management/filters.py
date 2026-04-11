# ================== FILTER SYSTEM (MEDIA SUPPORT FINAL) ==================
#remember file written by me but errors fixed via personal ai
import re
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI


mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
filters_db = db["filters"]


def add_filter(chat_id, trigger, data):
    filters_db.update_one(
        {"chat_id": chat_id, "trigger": trigger},
        {"$set": data},
        upsert=True
    )


def remove_filter(chat_id, trigger):
    filters_db.delete_one({"chat_id": chat_id, "trigger": trigger})


def get_filters(chat_id):
    return list(filters_db.find({"chat_id": chat_id}))


def remove_all(chat_id):
    filters_db.delete_many({"chat_id": chat_id})


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



@app.on_message(filters.command("filter") & filters.group)
async def addfilter(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply_text("ᴜsᴀɢᴇ:\n/filter <ᴛʀɪɢɢᴇʀ>")

    trigger = message.command[1].lower()
    
    if message.reply_to_message:

        reply = message.reply_to_message
        data = {}

        if reply.text:
            data = {"type": "text", "text": reply.text}

        elif reply.sticker:
            data = {"type": "sticker", "file_id": reply.sticker.file_id}

        elif reply.photo:
            data = {"type": "photo", "file_id": reply.photo.file_id}

        elif reply.video:
            data = {"type": "video", "file_id": reply.video.file_id}

        elif reply.animation:
            data = {"type": "gif", "file_id": reply.animation.file_id}

        elif reply.document:
            data = {"type": "document", "file_id": reply.document.file_id}

        else:
            return await message.reply_text("ᴜɴsᴜᴘᴘᴏʀᴛᴇᴅ ғᴏʀᴍᴀᴛ")

        add_filter(message.chat.id, trigger, data)

        return await message.reply_text(f"✅ ғɪʟᴛᴇʀ sᴀᴠᴇᴅ: `{trigger}`")

    if len(message.command) < 3:
        return await message.reply_text("ʀᴇᴘʟʏ ᴛᴏ ᴍᴇᴅɪᴀ ᴏʀ ɢɪᴠᴇ ᴛᴇxᴛ")

    reply_text = message.text.split(None, 2)[2]

    add_filter(message.chat.id, trigger, {
        "type": "text",
        "text": reply_text
    })

    await message.reply_text(f"✅ ғɪʟᴛᴇʀ ᴀᴅᴅᴇᴅ: `{trigger}`")


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


@app.on_message(filters.command("stop") & filters.group)
async def stopfilter(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply_text("ɢɪᴠᴇ ᴀ ᴛʀɪɢɢᴇʀ")

    trigger = message.command[1].lower()

    remove_filter(message.chat.id, trigger)

    await message.reply_text(f"❌ ʀᴇᴍᴏᴠᴇᴅ: `{trigger}`")


@app.on_message(filters.command("stopall") & filters.group)
async def stopall(client, message: Message):

    if not await is_admin(client, message):
        return await message.reply_text("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    remove_all(message.chat.id)

    await message.reply_text("🚫 ᴀʟʟ ғɪʟᴛᴇʀs ʀᴇᴍᴏᴠᴇᴅ")


@app.on_message(filters.group, group=2)
async def filter_reply(client, message: Message):

    if not (message.text or message.caption):
        return

    text = (message.text or message.caption).lower()
    data = get_filters(message.chat.id)

    for f in data:
        trigger = f["trigger"]

        if re.search(rf"\b{re.escape(trigger)}\b", text):

            try:
                if f["type"] == "text":
                    await message.reply_text(f["text"])

                elif f["type"] == "sticker":
                    await message.reply_sticker(f["file_id"])

                elif f["type"] == "photo":
                    await message.reply_photo(f["file_id"])

                elif f["type"] == "video":
                    await message.reply_video(f["file_id"])

                elif f["type"] == "gif":
                    await message.reply_animation(f["file_id"])

                elif f["type"] == "document":
                    await message.reply_document(f["file_id"])

            except:
                pass

            break
