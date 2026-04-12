import asyncio
import time
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app, userbot
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]

stats = db["vc_stats"]

active = {}
start_time = {}

def now():
    return datetime.now().strftime("%H:%M:%S")

async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False

def update_user(chat, user, join=0, speak=0, sec=0):
    stats.update_one(
        {"chat": chat, "user": user},
        {
            "$inc": {
                "joins": join,
                "speak": speak,
                "time": sec,
                "xp": (join * 5) + (speak * 2) + (sec // 10)
            }
        },
        upsert=True
    )

def get_top(chat, key):
    return list(stats.find({"chat": chat}).sort(key, -1).limit(5))

@app.on_message(filters.command("vcstart") & filters.group)
async def start(_, m: Message):
    active[m.chat.id] = set()
    start_time[m.chat.id] = {}
    await m.reply("🎙️ ᴠᴄ ᴛʀᴀᴄᴋɪɴɢ ᴏɴ")

@app.on_message(filters.command("vcend") & filters.group)
async def stop(_, m: Message):
    active.pop(m.chat.id, None)
    start_time.pop(m.chat.id, None)
    await m.reply("🛑 ᴠᴄ ᴛʀᴀᴄᴋɪɴɢ ᴏғғ")

@app.on_message(filters.command("vcleader") & filters.group)
async def leader(_, m: Message):
    data = get_top(m.chat.id, "xp")

    if not data:
        return await m.reply("❌ ɴᴏ ᴅᴀᴛᴀ")

    txt = "👑 ᴠᴄ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ\n\n"

    for i, d in enumerate(data, 1):
        txt += f"{i}. {d['user']} → {d.get('xp',0)} xp\n"

    await m.reply(txt)

@app.on_message(filters.command("vcstats") & filters.group)
async def stats_cmd(_, m: Message):
    user = m.from_user.id

    d = stats.find_one({"chat": m.chat.id, "user": user})

    if not d:
        return await m.reply("❌ ɴᴏ ᴅᴀᴛᴀ")

    txt = (
        "📊 ʏᴏᴜʀ ᴠᴄ sᴛᴀᴛs\n\n"
        f"🔁 ᴊᴏɪɴs: {d.get('joins',0)}\n"
        f"🎤 sᴘᴇᴀᴋ: {d.get('speak',0)}\n"
        f"⏱ ᴛɪᴍᴇ: {d.get('time',0)}s\n"
        f"⚡ xp: {d.get('xp',0)}"
    )

    await m.reply(txt)

@app.on_message(filters.command("vcpanel") & filters.group)
async def panel(_, m: Message):

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑", callback_data="top", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊", callback_data="graph", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("🧠", callback_data="ai", style=ButtonStyle.DANGER)
        ]
    ])

    await m.reply("🎙️ ᴠᴄ ᴘᴀɴᴇʟ", reply_markup=kb)

@app.on_callback_query()
async def cb(_, q):

    cid = q.message.chat.id

    if q.data == "top":
        data = get_top(cid, "xp")
        txt = "👑 ᴛᴏᴘ ᴠᴄ\n\n"
        for i, d in enumerate(data, 1):
            txt += f"{i}. {d['user']} → {d['xp']}\n"
        await q.message.reply(txt)

    elif q.data == "graph":
        data = get_top(cid, "speak")
        txt = "📊 sᴘᴇᴀᴋ ɢʀᴀᴘʜ\n\n"
        for d in data:
            bar = "█" * min(10, d.get("speak", 0))
            txt += f"{d['user']} {bar}\n"
        await q.message.reply(txt)

    elif q.data == "ai":
        data = get_top(cid, "xp")
        if not data:
            return await q.answer("ɴᴏ ᴅᴀᴛᴀ", True)

        top = data[0]

        txt = (
            "🧠 ᴀɪ ɪɴsɪɢʜᴛ\n\n"
            f"👑 ᴍᴏsᴛ ᴀᴄᴛɪᴠᴇ: {top['user']}\n"
            f"⚡ xp: {top['xp']}\n\n"
            "🎤 ᴇɴɢᴀɢᴇᴍᴇɴᴛ: ʜɪɢʜ"
        )

        await q.message.reply(txt)

async def watcher():
    await userbot.start()

    while True:
        for chat in list(active.keys()):
            try:
                call = await userbot.get_group_call(chat)
                parts = await userbot.get_group_call_participants(call.id)
            except:
                continue

            old = active.get(chat, set())
            new = set()

            for p in parts:
                uid = p.user_id
                if not uid:
                    continue

                new.add(uid)

                if getattr(p, "is_speaking", False):
                    update_user(chat, uid, speak=1)

            join = new - old
            left = old - new

            active[chat] = new

            for u in join:
                start_time[chat][u] = time.time()
                update_user(chat, u, join=1)
                await userbot.send_message(chat, f"➕ {u} joined vc")

            for u in left:
                dur = int(time.time() - start_time[chat].get(u, time.time()))
                update_user(chat, u, sec=dur)
                await userbot.send_message(chat, f"➖ {u} left vc")

        await asyncio.sleep(3)

asyncio.create_task(watcher())
