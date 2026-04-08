import os
import requests
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app


@app.on_message(filters.command("music"))
async def music(client, message: Message):
    msg = await message.reply("🔍 Searching...")

    # ❌ No query
    if len(message.command) < 2:
        return await msg.edit("❌ Usage: /music song name")

    query = " ".join(message.command[1:])

    try:
        # ✅ YOUR OWN API
        url = f"http://127.0.0.1:3000/api/search/songs?query={query}"
        res = requests.get(url, timeout=10).json()

        if not res.get("data") or not res["data"]["results"]:
            return await msg.edit("❌ No results found")

        song = res["data"]["results"][0]

        # 🎵 Extract data
        title = song["name"]
        artist = song["artists"]["primary"][0]["name"]
        thumb = song["image"][-1]["url"]
        audio_url = song["downloadUrl"][-1]["url"]

        file = f"{title}.mp4"

        await msg.edit("⬇️ Downloading...")

        # 🔥 Download audio
        audio = requests.get(audio_url, timeout=15).content
        with open(file, "wb") as f:
            f.write(audio)

        await msg.edit("📤 Uploading...")

        # 🎧 Send audio
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file,
            caption=f"🎵 {title}\n👤 {artist}",
            thumb=thumb
        )

        # 🧹 Cleanup
        os.remove(file)
        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Failed to fetch song")
