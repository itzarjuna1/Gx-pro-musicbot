
import asyncio
import time
from datetime import datetime

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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


def get_assistant():
    return userbot[0] if isinstance(userbot, list) else userbot


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
async def vcstart(_, m: Message):
    active[m.chat.id] = set()
    start_time[m.chat.id] = {}
    await m.reply("🎙️ ᴠᴄ ᴛʀᴀᴄᴋɪɴɢ ᴏɴ")


@app.on_message(filters.command("vcend") & filters.group)
async def vcend(_, m: Message):
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


@app.on_message(filters.command("vcpanel") & filters.group)
async def panel(_, m: Message):

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("👑", callback_data="vc_top", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("📊", callback_data="vc_graph", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("🧠", callback_data="vc_ai", style=ButtonStyle.DANGER)
        ]
    ])

    await m.reply("🎙️ ᴠᴄ ᴘᴀɴᴇʟ", reply_markup=kb)


@app.on_callback_query(filters.regex("^vc_"))
async def vc_buttons(_, q: CallbackQuery):

    cid = q.message.chat.id
    await q.answer()

    if q.data == "vc_top":
        data = get_top(cid, "xp")
        txt = "👑 ᴛᴏᴘ ᴠᴄ\n\n"
        for i, d in enumerate(data, 1):
            txt += f"{i}. {d['user']} → {d.get('xp',0)}\n"
        await q.message.reply(txt)

    elif q.data == "vc_graph":
        data = get_top(cid, "speak")
        txt = "📊 sᴘᴇᴀᴋ\n\n"
        for d in data:
            bar = "█" * min(10, d.get("speak", 0))
            txt += f"{d['user']} {bar}\n"
        await q.message.reply(txt)

    elif q.data == "vc_ai":
        data = get_top(cid, "xp")
        if not data:
            return await q.answer("ɴᴏ ᴅᴀᴛᴀ", True)

        top = data[0]

        txt = (
            "🧠 ᴀɪ ɪɴsɪɢʜᴛ\n\n"
            f"👑 ᴍᴏsᴛ ᴀᴄᴛɪᴠᴇ: {top['user']}\n"
            f"⚡ xp: {top['xp']}\n"
        )

        await q.message.reply(txt)


async def watcher():
    client = get_assistant()

    while True:
        try:
            for chat in list(active.keys()):

                try:
                    call = await client.get_group_call(chat)
                    parts = await client.get_group_call_participants(call.id)
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

                joined = new - old
                left = old - new

                active[chat] = new

                for u in joined:
                    start_time[chat][u] = time.time()
                    update_user(chat, u, join=1)
                    await client.send_message(chat, f"➕ {u} joined vc")

                for u in left:
                    dur = int(time.time() - start_time[chat].get(u, time.time()))
                    update_user(chat, u, sec=dur)
                    await client.send_message(chat, f"➖ {u} left vc")

            await asyncio.sleep(3)

        except Exception as e:
            print(e)
            await asyncio.sleep(5)


asyncio.create_task(watcher())
