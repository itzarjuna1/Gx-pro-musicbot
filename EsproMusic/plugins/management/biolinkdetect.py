import re
import asyncio
from pymongo import MongoClient

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from EsproMusic import app
from config import MONGO_DB_URI


mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
bio_db = db["biolink"]


LINK_REGEX = re.compile(
    r"(https?://|t\.me/|www\.|\.com|\.net|\.org)",
    re.IGNORECASE
)


def get_cfg(chat_id):
    data = bio_db.find_one({"chat": chat_id})
    if not data:
        return {"enabled": False}
    return data


def set_cfg(chat_id, value):
    bio_db.update_one(
        {"chat": chat_id},
        {"$set": {"enabled": value}},
        upsert=True
    )


async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

@app.on_message(filters.command("biolink") & filters.group)
async def toggle_biolink(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➜ /biolink on/off")

    arg = message.command[1].lower()

    if arg == "on":
        set_cfg(message.chat.id, True)
        await message.reply("🔗 ʙɪᴏ ʟɪɴᴋ ʙʟᴏᴄᴋᴇʀ ᴇɴᴀʙʟᴇᴅ")

    elif arg == "off":
        set_cfg(message.chat.id, False)
        await message.reply("🔗 ʙɪᴏ ʟɪɴᴋ ʙʟᴏᴄᴋᴇʀ ᴅɪsᴀʙʟᴇᴅ")

@app.on_message(filters.group & filters.text)
async def bio_link_blocker(client, message: Message):

    cfg = get_cfg(message.chat.id)

    if not cfg.get("enabled"):
        return

    user = message.from_user
    if not user:
        return

    if await is_admin(client, message.chat.id, user.id):
        return

    try:
        full_user = await client.get_users(user.id)
        bio = full_user.bio or ""

        if LINK_REGEX.search(bio):

            try:
                await message.delete()
            except:
                pass

            warn = await client.send_message(
                message.chat.id,
                f"⚠️ ʜᴇʏ {user.mention}, ʙɪᴏ ʟɪɴᴋs ᴀʀᴇ ɴᴏᴛ ᴀʟʟᴏᴡᴇᴅ ɪɴ ᴛʜɪs ɢʀᴏᴜᴘ.\n"
                f"ʀᴇᴍᴏᴠᴇ ɪᴛ ғʀᴏᴍ ʏᴏᴜʀ ʙɪᴏ."
            )

            await asyncio.sleep(5)

            try:
                await warn.delete()
            except:
                pass

    except:
        pass
