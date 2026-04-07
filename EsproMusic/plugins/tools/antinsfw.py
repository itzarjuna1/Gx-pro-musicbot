import os
import asyncio
import subprocess
from PIL import Image
import httpx

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, MessageDeleteForbidden

from EsproMusic import app
from EsproMusic.core.mongo import groups, NSFW, NSFW_STORAGE
from EsproMusic.utils.nexa_check import admin_check
from EsproMusic.utils.staff import staff_or_owner

os.makedirs("temp", exist_ok=True)

HF_NSFW_API = "https://nexacoders-nexa-api.hf.space/scan"
API4AI_URL = "https://demo.api4ai.cloud/nsfw/v1/results"
API4AI_KEY = "a4a-p3htHPSXFeCnvAZ21nLkRtRPGUFFTaJV"

TIMEOUT = httpx.Timeout(20.0, connect=10.0)

THRESHOLD = {
    "porn": 50,
    "hentai": 50,
    "sexy": 60
}


def extract_media(msg: Message):
    return (
        msg.photo or msg.video or msg.animation or msg.sticker or
        (msg.document if msg.document and msg.document.mime_type == "image/gif" else None)
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


@app.on_message(filters.command("nsfw") & filters.group)
async def toggle(client, message: Message):
    if not await admin_check(message):
        return await message.reply("Admins only")

    if len(message.command) < 2:
        return await message.reply("/nsfw on or off")

    state = message.command[1].lower()

    await groups.update_one(
        {"_id": message.chat.id},
        {"$set": {"nsfw": state == "on"}},
        upsert=True
    )

    await message.reply(f"NSFW {'ON' if state=='on' else 'OFF'}")


@app.on_message(filters.command("scan") & filters.group)
async def scan_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to media")

    r = await scan_media(message.reply_to_message)

    if "error" in r:
        return await message.reply("Error scanning")

    d = r["results"]

    await message.reply(
        f"NSFW 🔞\n\nPorn: {d['porn']:.1f}%\nHentai: {d['hentai']:.1f}%\nSexy: {d['sexy']:.1f}%"
    )


@app.on_message((filters.photo | filters.video | filters.animation | filters.sticker) & filters.group, group=-1)
async def auto(client, message: Message):
    grp = await groups.find_one({"_id": message.chat.id})
    if not grp or not grp.get("nsfw"):
        return

    r = await scan_media(message)

    if "error" in r or r.get("sfw"):
        return

    try:
        warn = await message.reply("🚫 NSFW detected & removed")
        await message.delete()
    except (RPCError, MessageDeleteForbidden):
        return

    await asyncio.sleep(10)
    try:
        await warn.delete()
    except:
        pass


@app.on_message(filters.command("marknsfw"))
@staff_or_owner
async def mark_nsfw(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("Reply to media")

    media = extract_media(message.reply_to_message)
    fid = media.file_unique_id

    await NSFW.update_one(
        {"_id": fid},
        {"$set": {"sfw": False}},
        upsert=True
    )

    try:
        await message.reply_to_message.forward(NSFW_STORAGE)
    except:
        pass

    await message.reply("Marked NSFW")


@app.on_message(filters.command("unmarknsfw"))
@staff_or_owner
async def unmark(client, message: Message):
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
