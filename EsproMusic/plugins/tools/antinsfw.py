
import os
import asyncio
import subprocess
from PIL import Image
import httpx

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, MessageDeleteForbidden
from pyrogram.enums import ChatMemberStatus

from EsproMusic import app
from EsproMusic.core.mongo import groups, NSFW, NSFW_STORAGE

os.makedirs("temp", exist_ok=True)

# ================= ADMIN CHECK =================
async def is_admin(client, message: Message):
    try:
        if not message.from_user:
            return False

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

# ================= NSFW APIs ====================
HF_NSFW_API = "https://nexacoders-nexa-api.hf.space/scan"
API4AI_URL = "https://demo.api4ai.cloud/nsfw/v1/results"
API4AI_KEY = "a4a-p3htHPSXFeCnvAZ21nLkRtRPGUFFTaJV"

TIMEOUT = httpx.Timeout(20.0, connect=10.0)

# 🔥 LOWERED THRESHOLD (better detection)
THRESHOLD = {
    "porn": 30,
    "hentai": 30,
    "sexy": 40
}


def extract_media(msg: Message):
    return (
        msg.photo or msg.video or msg.animation or msg.sticker or
        msg.document
    )


async def process_sticker(message: Message, fid: str):
    tmp = await message.download(f"temp/{fid}")

    if tmp.endswith(".webp"):
        img = Image.open(tmp).convert("RGB")
        path = f"temp/{fid}.jpg"
        img.save(path, "JPEG")
        os.remove(tmp)
        return path

    if tmp.endswith(".tgs"):
        os.remove(tmp)
        return None

    return tmp


async def scan_hf(path):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(path, "rb") as f:
                r = await client.post(HF_NSFW_API, files={"file": f})
        if r.status_code != 200:
            return None
        s = r.json().get("scores", {})
        return {
            "porn": s.get("porn", 0) * 100,
            "hentai": s.get("hentai", 0) * 100,
            "sexy": s.get("sexy", 0) * 100,
        }
    except:
        return None


async def scan_api4ai(path):
    try:
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            with open(path, "rb") as f:
                r = await client.post(
                    API4AI_URL,
                    headers={"A4AI-KEY": API4AI_KEY},
                    files={"image": f}
                )
        if r.status_code != 200:
            return None
        data = r.json()
        e = data["results"][0]["entities"][0]["classes"]
        return {
            "porn": e.get("porn", 0) * 100,
            "hentai": e.get("hentai", 0) * 100,
            "sexy": e.get("sexual", 0) * 100,
        }
    except:
        return None


def is_nsfw(res):
    return (
        res["porn"] >= THRESHOLD["porn"] or
        res["hentai"] >= THRESHOLD["hentai"] or
        res["sexy"] >= THRESHOLD["sexy"]
    )


async def scan_media(message: Message):
    media = extract_media(message)
    if not media:
        return {"error": True}

    fid = media.file_unique_id
    cached = await NSFW.find_one({"_id": fid})
    if cached:
        return cached

    path = None

    try:
        if message.photo:
            path = await message.download(f"temp/{fid}.jpg")

        elif message.sticker:
            path = await process_sticker(message, fid)
            if not path:
                return {"_id": fid, "sfw": False, "results": {"porn": 100, "hentai": 100, "sexy": 100}}

        else:
            tmp = await message.download(f"temp/{fid}")
            path = f"temp/{fid}.jpg"

            subprocess.run(
                ["ffmpeg", "-i", tmp, "-frames:v", "1", path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            if os.path.exists(tmp):
                os.remove(tmp)

        hf, api = await asyncio.gather(scan_hf(path), scan_api4ai(path))

        if not hf and not api:
            return {"error": True}

        def best(k):
            return max((hf or {}).get(k, 0), (api or {}).get(k, 0))

        results = {
            "porn": best("porn"),
            "hentai": best("hentai"),
            "sexy": best("sexy"),
        }

        sfw = not is_nsfw(results)

        doc = {
            "_id": fid,
            "results": results,
            "sfw": sfw
        }

        await NSFW.update_one({"_id": fid}, {"$set": doc}, upsert=True)

        if not sfw:
            try:
                await message.forward(NSFW_STORAGE)
            except:
                pass

        return doc

    finally:
        if path and os.path.exists(path):
            os.remove(path)


# ================= COMMANDS =================

@app.on_message(filters.command("nsfw") & filters.group)
async def toggle(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("❌ admins only")

    if len(message.command) < 2:
        return await message.reply("Usage: /nsfw enable or disable")

    state = message.command[1].lower()

    if state not in ["enable", "disable"]:
        return await message.reply("Use: enable or disable")

    await groups.update_one(
        {"_id": message.chat.id},
        {"$set": {"nsfw": state == "enable"}},
        upsert=True
    )

    await message.reply(f"NSFW {'ENABLED' if state=='enable' else 'DISABLED'}")


@app.on_message(filters.command("nsfwstatus") & filters.group)
async def status(client, message: Message):
    grp = await groups.find_one({"_id": message.chat.id})
    state = grp.get("nsfw") if grp else False
    await message.reply(f"NSFW is {'ENABLED' if state else 'DISABLED'}")


@app.on_message(filters.command("scan") & filters.group)
async def scan_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to media")

    r = await scan_media(message.reply_to_message)

    if "error" in r:
        return await message.reply("Scan failed")

    d = r["results"]

    await message.reply(
        f"NSFW Result 🔞\n\n"
        f"Porn: {d['porn']:.1f}%\n"
        f"Hentai: {d['hentai']:.1f}%\n"
        f"Sexy: {d['sexy']:.1f}%\n\n"
        f"Status: {'NSFW' if not r['sfw'] else 'SAFE'}"
    )


@app.on_message(filters.command("marknsfw") & filters.group)
async def mark(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("❌ admins only")

    if not message.reply_to_message:
        return await message.reply("Reply to media")

    media = extract_media(message.reply_to_message)
    fid = media.file_unique_id

    await NSFW.update_one(
        {"_id": fid},
        {"$set": {"sfw": False}},
        upsert=True
    )

    await message.reply("Marked NSFW")


@app.on_message(filters.command("unmarknsfw") & filters.group)
async def unmark(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("❌ admins only")

    if not message.reply_to_message:
        return await message.reply("Reply to media")

    media = extract_media(message.reply_to_message)
    fid = media.file_unique_id

    await NSFW.update_one(
        {"_id": fid},
        {"$set": {"sfw": True}},
        upsert=True
    )

    await message.reply("Marked SAFE")


# ================= AUTO FILTER =================

@app.on_message(
    (filters.photo | filters.video | filters.animation | filters.sticker | filters.document)
    & filters.group,
    group=0
)
async def auto(client, message: Message):
    grp = await groups.find_one({"_id": message.chat.id})

    if not grp or not grp.get("nsfw"):
        return

    r = await scan_media(message)

    if "error" in r or r.get("sfw"):
        return

    try:
        await message.delete()
        warn = await message.reply("🚫 NSFW detected & removed")
    except (RPCError, MessageDeleteForbidden):
        return

    await asyncio.sleep(5)
    try:
        await warn.delete()
    except:
        pass
