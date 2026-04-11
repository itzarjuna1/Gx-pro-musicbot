# ================== GOOGLE SEARCH SYSTEM ==================

import aiohttp
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app


# ================== SEARCH FUNCTION ==================
async def search_web(query):
    url = f"https://api.duckduckgo.com/?q={query}&format=json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()

    # Priority 1: direct answer
    if data.get("AbstractText"):
        return data["AbstractText"]

    # Priority 2: instant answer
    if data.get("Answer"):
        return data["Answer"]

    # Priority 3: heading + related
    if data.get("Heading"):
        return data["Heading"]

    return "❌ ɴᴏ ᴀɴsᴡᴇʀ ғᴏᴜɴᴅ"


# ================== COMMAND ==================
@app.on_message(filters.command("google") & filters.group)
async def google_search(client, message: Message):
    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /google <ǫᴜᴇʀʏ>")

    query = message.text.split(None, 1)[1]

    msg = await message.reply("🔎 sᴇᴀʀᴄʜɪɴɢ...")

    try:
        result = await search_web(query)

        await msg.edit(
            f"🔎 ǫᴜᴇʀʏ: {query}\n\n"
            f"💡 ᴀɴsᴡᴇʀ:{result}"
        )

    except Exception as e:
        await msg.edit("❌ ғᴀɪʟᴇᴅ ᴛᴏ ғᴇᴛᴄʜ ʀᴇsᴜʟᴛ")
