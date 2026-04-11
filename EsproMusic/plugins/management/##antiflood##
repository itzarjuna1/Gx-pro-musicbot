import time
from collections import defaultdict

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, ChatPermissions
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
flood_db = db["antiflood"]

user_msgs = defaultdict(list)

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

def parse_time(t):
    unit = t[-1]
    num = int(t[:-1])
    if unit == "s":
        return num
    if unit == "m":
        return num * 60
    if unit == "h":
        return num * 3600
    if unit == "d":
        return num * 86400
    return 0

def get_settings(chat_id):
    data = flood_db.find_one({"chat_id": chat_id})
    return data if data else {}

def panel(chat_id):
    data = get_settings(chat_id)
    count = data.get("count", 0)
    mode = data.get("mode", "mute")

    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(f"🔢 ʟɪᴍɪᴛ: {count}", callback_data="noop", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton(f"⚙️ ᴍᴏᴅᴇ: {mode}", callback_data="noop", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("➕ ɪɴᴄʀᴇᴀsᴇ", callback_data="inc", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("➖ ᴅᴇᴄʀᴇᴀsᴇ", callback_data="dec", style=ButtonStyle.DANGER)
        ],
        [
            InlineKeyboardButton("❌ ᴅɪsᴀʙʟᴇ", callback_data="off", style=ButtonStyle.DANGER)
        ]
    ])

@app.on_message(filters.command("flood") & filters.group)
async def flood_status(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return
    await message.reply("📊 ᴀɴᴛɪғʟᴏᴏᴅ ᴘᴀɴᴇʟ", reply_markup=panel(message.chat.id))

@app.on_callback_query()
async def flood_buttons(client, query):
    chat_id = query.message.chat.id

    if not await is_admin(client, chat_id, query.from_user.id):
        return await query.answer("ᴀᴅᴍɪɴs ᴏɴʟʏ", show_alert=True)

    data = get_settings(chat_id)
    count = data.get("count", 0)

    if query.data == "inc":
        count += 1
    elif query.data == "dec":
        count = max(0, count - 1)
    elif query.data == "off":
        count = 0

    flood_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"count": count}},
        upsert=True
    )

    await query.message.edit_reply_markup(panel(chat_id))
    await query.answer("ᴜᴘᴅᴀᴛᴇᴅ")

@app.on_message(filters.command("setflood") & filters.group)
async def setflood(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    arg = message.command[1].lower()

    if arg in ["off", "no", "0"]:
        flood_db.update_one({"chat_id": message.chat.id}, {"$set": {"count": 0}}, upsert=True)
        return await message.reply("✅ ᴀɴᴛɪғʟᴏᴏᴅ ᴅɪsᴀʙʟᴇᴅ")

    flood_db.update_one({"chat_id": message.chat.id}, {"$set": {"count": int(arg)}}, upsert=True)
    await message.reply(f"✅ ʟɪᴍɪᴛ sᴇᴛ ᴛᴏ {arg}")

@app.on_message(filters.command("floodmode") & filters.group)
async def floodmode(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    mode = message.command[1]
    extra = message.command[2] if len(message.command) > 2 else None

    flood_db.update_one(
        {"chat_id": message.chat.id},
        {"$set": {"mode": mode, "extra": extra}},
        upsert=True
    )

    await message.reply(f"✅ ᴍᴏᴅᴇ sᴇᴛ ᴛᴏ {mode}")

@app.on_message(filters.group, group=2)
async def antiflood(client, message: Message):
    if not message.from_user:
        return

    chat_id = message.chat.id
    user_id = message.from_user.id

    if await is_admin(client, chat_id, user_id):
        return

    data = get_settings(chat_id)
    limit = data.get("count", 0)

    if not limit:
        return

    now = time.time()
    user_msgs[(chat_id, user_id)].append(now)

    msgs = user_msgs[(chat_id, user_id)]

    if len(msgs) > limit:
        mode = data.get("mode", "mute")
        extra = data.get("extra")

        try:
            if mode == "ban":
                await client.ban_chat_member(chat_id, user_id)

            elif mode == "kick":
                await client.ban_chat_member(chat_id, user_id)
                await client.unban_chat_member(chat_id, user_id)

            elif mode == "mute":
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions()
                )

            elif mode == "tban":
                duration = parse_time(extra)
                until = int(time.time()) + duration
                await client.ban_chat_member(chat_id, user_id, until_date=until)

            elif mode == "tmute":
                duration = parse_time(extra)
                until = int(time.time()) + duration
                await client.restrict_chat_member(
                    chat_id,
                    user_id,
                    ChatPermissions(),
                    until_date=until
                )

            await message.reply("🚫 ғʟᴏᴏᴅ ᴅᴇᴛᴇᴄᴛᴇᴅ")

        except:
            pass

        user_msgs[(chat_id, user_id)] = []
