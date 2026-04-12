import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
vc_db = db["vclogger"]
stats_db = db["vcstats"]


def now():
    return datetime.now().strftime("%H:%M:%S")


async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False


def get_cfg(chat_id):
    d = vc_db.find_one({"chat_id": chat_id})
    if not d:
        return {"time": 5, "auto": True}
    return d


def set_time(chat_id, t):
    vc_db.update_one({"chat_id": chat_id}, {"$set": {"time": t}}, upsert=True)


def set_auto(chat_id, v):
    vc_db.update_one({"chat_id": chat_id}, {"$set": {"auto": v}}, upsert=True)


def add_stat(chat_id, user_id):
    stats_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"joins": 1}},
        upsert=True
    )


def get_top(chat_id):
    return list(
        stats_db.find({"chat_id": chat_id})
        .sort("joins", -1)
        .limit(5)
    )


@app.on_message(filters.command("vclog") & filters.group)
async def panel(client, message: Message):
    cfg = get_cfg(message.chat.id)

    txt = (
        "🎙️ ᴠᴄ ᴄᴏɴᴛʀᴏʟ\n\n"
        f"⏱ ᴅᴇʟᴇᴛᴇ: {cfg.get('time',5)}s\n"
        f"⚙️ ᴀᴜᴛᴏ: {'ᴏɴ' if cfg.get('auto',True) else 'ᴏғғ'}"
    )

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱ ᴛɪᴍᴇ", callback_data="vctime", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⚙️ ᴛᴏɢɢʟᴇ", callback_data="vctoggle", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("👑 ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ", callback_data="vcleader", style=ButtonStyle.PRIMARY)
        ],
        [
            InlineKeyboardButton("🧠 ɪɴsɪɢʜᴛ", callback_data="vcai", style=ButtonStyle.DANGER)
        ]
    ])

    await message.reply(txt, reply_markup=btn)


@app.on_callback_query(filters.regex("^vctime$"))
async def time_menu(client, q):
    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("5s", callback_data="set_5", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("10s", callback_data="set_10", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("20s", callback_data="set_20", style=ButtonStyle.DANGER)
        ]
    ])
    await q.message.reply("⏱ sᴇʟᴇᴄᴛ ᴛɪᴍᴇ", reply_markup=kb)


@app.on_callback_query(filters.regex("^set_"))
async def set_time_cb(client, q):
    t = int(q.data.split("_")[1])
    set_time(q.message.chat.id, t)
    await q.answer("ᴜᴘᴅᴀᴛᴇᴅ")


@app.on_callback_query(filters.regex("^vctoggle$"))
async def toggle_cb(client, q):
    cfg = get_cfg(q.message.chat.id)
    new = not cfg.get("auto", True)
    set_auto(q.message.chat.id, new)
    await q.answer("ᴏɴ" if new else "ᴏғғ")


@app.on_callback_query(filters.regex("^vcleader$"))
async def leader(client, q):
    data = get_top(q.message.chat.id)

    if not data:
        return await q.answer("ɴᴏ ᴅᴀᴛᴀ", show_alert=True)

    text = "👑 ᴠᴄ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ\n\n"

    for i, d in enumerate(data, 1):
        text += f"{i}. {d['user_id']} → {d.get('joins',0)}\n"

    await q.message.reply(text)


@app.on_callback_query(filters.regex("^vcai$"))
async def ai(client, q):
    data = get_top(q.message.chat.id)

    if not data:
        return await q.answer("ɴᴏ ᴅᴀᴛᴀ", show_alert=True)

    top = data[0]

    text = (
        "🧠 ᴠᴄ ɪɴsɪɢʜᴛ\n\n"
        f"👑 ᴍᴏsᴛ ᴀᴄᴛɪᴠᴇ: {top['user_id']}\n"
        f"📊 ᴊᴏɪɴs: {top.get('joins',0)}\n\n"
        "🎤 ᴀᴄᴛɪᴠɪᴛʏ: ʜɪɢʜ\n"
        "📶 ᴇɴɢᴀɢᴇᴍᴇɴᴛ: sᴛᴀʙʟᴇ"
    )

    await q.message.reply(text)


@app.on_message(filters.group & filters.service)
async def logger(client, message: Message):

    try:
        cfg = get_cfg(message.chat.id)

        txt = None
        delete = False

        if message.video_chat_started:
            txt = f"🎙️ ᴠᴄ sᴛᴀʀᴛᴇᴅ\n⏰ {now()}"

        elif message.video_chat_ended:
            txt = f"🔴 ᴠᴄ ᴇɴᴅᴇᴅ\n⏰ {now()}"

        elif message.new_chat_members:
            u = message.new_chat_members[0]
            txt = f"➕ {u.first_name} ᴊᴏɪɴᴇᴅ"
            delete = True
            add_stat(message.chat.id, u.id)

        elif message.left_chat_member:
            u = message.left_chat_member
            txt = f"➖ {u.first_name} ʟᴇғᴛ"
            delete = True

        if not txt:
            return

        m = await message.reply(txt)

        if delete and cfg.get("auto", True):
            await asyncio.sleep(cfg.get("time", 5))
            try:
                await m.delete()
            except:
                pass

    except:
        pass
