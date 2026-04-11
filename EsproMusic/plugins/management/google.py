import aiohttp
from bs4 import BeautifulSoup
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app


async def search_web(query):
    url = f"https://html.duckduckgo.com/html/?q={query}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as resp:
            html = await resp.text()

    soup = BeautifulSoup(html, "html.parser")

    results = []

    for result in soup.find_all("a", class_="result__a", limit=3):
        title = result.get_text()
        link = result.get("href")

        results.append(f"🔗 {title}\n{link}")

    if not results:
        return "❌ ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ"

    return "\n\n".join(results)

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
            f"📄 ʀᴇsᴜʟᴛs:{result}"
        )

    except Exception as e:
        await msg.edit("❌ ᴇʀʀᴏʀ ғᴇᴛᴄʜɪɴɢ ʀᴇsᴜʟᴛs")
