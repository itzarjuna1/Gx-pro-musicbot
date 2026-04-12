import asyncio
from datetime import datetime
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient
from pytgcalls import PyTgCalls
from pytgcalls.types import Update

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
vc_db = db["vclogger"]
stats_db = db["vcstats"]
speak_db = db["vcspeak"]

vc = PyTgCalls(app)

active_calls = {}
user_activity = {}


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
    return d if d else {"time": 5, "auto": True}


def set_time(chat_id, t):
    vc_db.update_one({"chat_id": chat_id}, {"$set": {"time": t}}, upsert=True)


def set_auto(chat_id, v):
    vc_db.update_one({"chat_id": chat_id}, {"$set": {"auto": v}}, upsert=True)


def add_join(chat_id, user_id):
    stats_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"joins": 1}},
        upsert=True
    )


def add_speak(chat_id, user_id):
    speak_db.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$inc": {"speak": 1}},
        upsert=True
    )


def top_join(chat_id):
    return list(stats_db.find({"chat_id": chat_id}).sort("joins", -1).limit(5))


def top_speak(chat_id):
    return list(speak_db.find({"chat_id": chat_id}).sort("speak", -1).limit(5))


@app.on_message(filters.command("vclog") & filters.group)
async def panel(client, message: Message):
    cfg = get_cfg(message.chat.id)

    txt = (
        "🎙️ ᴠᴄ ᴄᴏɴᴛʀᴏʟ\n\n"
        f"⏱ {cfg.get('time',5)}s\n"
        f"⚙️ {'ᴏɴ' if cfg.get('auto',True) else 'ᴏғғ'}"
    )

    btn = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏱", callback_data="vctime", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("⚙️", callback_data="vctoggle", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("👑 joins", callback_data="vcleader", style=ButtonStyle.PRIMARY),
            InlineKeyboardButton("🎤 speak", callback_data="vcspeak", style=ButtonStyle.SUCCESS)
        ],
        [
            InlineKeyboardButton("📊 graph", callback_data="vcgraph", style=ButtonStyle.DANGER)
        ]
    ])

    await message.reply(txt, reply_markup=btn)


@app.on_callback_query(filters.regex("^vc"))
async def cb(client, q):

    cid = q.message.chat.id

    if q.data == "vctime":
        kb = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("5", callback_data="set_5", style=ButtonStyle.PRIMARY),
                InlineKeyboardButton("10", callback_data="set_10", style=ButtonStyle.SUCCESS),
                InlineKeyboardButton("20", callback_data="set_20", style=ButtonStyle.DANGER)
            ]
        ])
        await q.message.reply("⏱ time", reply_markup=kb)
        return await q.answer()

    if q.data.startswith("set_"):
        set_time(cid, int(q.data.split("_")[1]))
        return await q.answer("done")

    if q.data == "vctoggle":
        cfg = get_cfg(cid)
        new = not cfg.get("auto", True)
        set_auto(cid, new)
        return await q.answer("on" if new else "off")

    if q.data == "vcleader":
        data = top_join(cid)
        if not data:
            return await q.answer("no data", show_alert=True)

        txt = "👑 joins\n\n"
        for i, d in enumerate(data, 1):
            txt += f"{i}. {d['user_id']} → {d.get('joins',0)}\n"

        await q.message.reply(txt)
        return await q.answer()

    if q.data == "vcspeak":
        data = top_speak(cid)
        if not data:
            return await q.answer("no data", show_alert=True)

        txt = "🎤 speaking\n\n"
        for i, d in enumerate(data, 1):
            txt += f"{i}. {d['user_id']} → {d.get('speak',0)}\n"

        await q.message.reply(txt)
        return await q.answer()

    if q.data == "vcgraph":
        data = top_speak(cid)
        if not data:
            return await q.answer("no data", show_alert=True)

        txt = "📊 activity\n\n"
        for d in data:
            bars = "█" * min(10, d.get("speak", 0))
            txt += f"{d['user_id']} {bars}\n"

        await q.message.reply(txt)
        return await q.answer()


@app.on_message(filters.command("vcmembers") & filters.group)
async def members(client, message: Message):
    cid = message.chat.id

    if cid not in active_calls or not active_calls[cid]:
        return await message.reply("❌ no active vc")

    txt = "🎧 vc members\n\n"

    for uid in active_calls[cid]:
        try:
            user = await app.get_users(uid)
            txt += f"• {user.first_name}\n"
        except:
            txt += f"• {uid}\n"

    await message.reply(txt)


@vc.on_update()
async def vc_events(_, update: Update):

    if update.__class__.__name__ != "UpdateGroupCallParticipants":
        return

    cid = update.call.chat_id
    participants = update.participants

    if cid not in active_calls:
        active_calls[cid] = set()

    old = active_calls[cid]
    new = set()

    for p in participants:
        if not p.user_id:
            continue

        new.add(p.user_id)

        if getattr(p, "action", None) == "speaking":
            add_speak(cid, p.user_id)

    joined = new - old
    left = old - new

    active_calls[cid] = new

    for uid in joined:
        try:
            user = await app.get_users(uid)
            add_join(cid, uid)
            msg = await app.send_message(cid, f"➕ {user.first_name}")
            await asyncio.sleep(5)
            await msg.delete()
        except:
            pass

    for uid in left:
        try:
            user = await app.get_users(uid)
            msg = await app.send_message(cid, f"➖ {user.first_name}")
            await asyncio.sleep(5)
            await msg.delete()
        except:
            pass


async def start_vc():
    await vc.start()


asyncio.create_task(start_vc())
