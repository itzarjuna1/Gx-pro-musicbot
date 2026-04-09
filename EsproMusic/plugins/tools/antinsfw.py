import os
import asyncio
import subprocess
from PIL import Image
import httpx

from lottie.importers import import_tgs
from lottie.exporters import export_png

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.errors import RPCError, MessageDeleteForbidden
from pyrogram.enums import ChatMemberStatus

from EsproMusic import app
from EsproMusic.core.mongo import groups, NSFW, NSFW_STORAGE

os.makedirs("temp", exist_ok=True)

HF_NSFW_API = "https://nexacoders-nexa-api.hf.space/scan"
API4AI_URL = "https://demo.api4ai.cloud/nsfw/v1/results"
API4AI_KEY = "a4a-p3htHPSXFeCnvAZ21nLkRtRPGUFFTaJV"

TIMEOUT = httpx.Timeout(20.0, connect=10.0)

THRESHOLD = {
    "porn": 3,
    "hentai": 3,
    "sexy": 5
}


# ================= ADMIN =================
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


def extract_media(msg: Message):
    return (
        msg.photo or msg.video or msg.animation or msg.sticker or msg.document
    )


# ================= STICKER (ADVANCED) =================
async def process_sticker(message: Message, fid: str):
    tmp = await message.download(f"temp/{fid}")

    # static sticker
    if tmp.endswith(".webp"):
        try:
            img = Image.open(tmp).convert("RGB")
            path = f"temp/{fid}.jpg"
            img.save(path, "JPEG")
            os.remove(tmp)
            return path
        except:
            os.remove(tmp)
            return None

    # animated sticker (.tgs → png)
    if tmp.endswith(".tgs"):
        try:
            anim = import_tgs(tmp)
            path = f"temp/{fid}.png"
            export_png(anim, path, frame=0)
            os.remove(tmp)
            return path
        except:
            os.remove(tmp)
            return None

    return tmp


# ================= API =================
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
    # 🔥 slightly stronger hentai detection
    if res["hentai"] > 2:
        return True

    return (
        res["porn"] >= THRESHOLD["porn"] or
        res["hentai"] >= THRESHOLD["hentai"] or
        res["sexy"] >= THRESHOLD["sexy"]
    )


# ================= SCAN =================
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

            if not path or not os.path.exists(path):
                return {"error": True}

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
        return await message.reply("admins only")

    if len(message.command) < 2:
        return await message.reply("/nsfw on or off")

    state = message.command[1].lower()

    await groups.update_one(
        {"_id": message.chat.id},
        {"$set": {"nsfw": state == "on"}},
        upsert=True
    )

    await message.reply(f"nsfw {'on' if state=='on' else 'off'}")


@app.on_message(filters.command("scan") & filters.group)
async def scan_cmd(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("reply to media")

    r = await scan_media(message.reply_to_message)

    if "error" in r:
        return await message.reply("scan failed")

    d = r["results"]

    await message.reply(
        f"nsfw\n\nporn: {d['porn']:.1f}%\n"
        f"hentai: {d['hentai']:.1f}%\n"
        f"sexy: {d['sexy']:.1f}%"
    )


# 🔥 blacklist sticker pack
@app.on_message(filters.command("blsticker") & filters.group)
async def bl_sticker(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("admins only")

    if not message.reply_to_message or not message.reply_to_message.sticker:
        return await message.reply("reply to a sticker")

    pack = message.reply_to_message.sticker.set_name

    if not pack:
        return await message.reply("no pack found")

    await groups.update_one(
        {"_id": message.chat.id},
        {"$addToSet": {"bl_stickers": pack}},
        upsert=True
    )

    await message.reply("sticker pack blacklisted")


# ================= AUTO =================

@app.on_message(
    (filters.photo | filters.video | filters.animation | filters.sticker | filters.document)
    & filters.group,
    group=0
)
async def auto(client, message: Message):
    grp = await groups.find_one({"_id": message.chat.id})

    if not grp or not grp.get("nsfw"):
        return

    # 🔥 pack blacklist
    if message.sticker:
        pack = message.sticker.set_name
        if pack and pack in grp.get("bl_stickers", []):
            try:
                await message.delete()
                return
            except:
                return

    r = await scan_media(message)

    if "error" in r or r.get("sfw"):
        return

    try:
        await message.delete()
        warn = await message.reply("nsfw detected & removed")
    except (RPCError, MessageDeleteForbidden):
        return

    await asyncio.sleep(5)
    try:
        await warn.delete()
    except:
        pass
