import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app


@app.on_message(filters.command("music"))
async def saavn_music(client: Client, message: Message):
    msg = await message.reply("🦋")

    if len(message.command) < 2:
        return await msg.edit("Usage: /music song name")

    query = " ".join(message.command[1:])

    try:
        # 🔥 Search API
        url = f"https://saavn.dev/api/search/songs?query={query}"
        res = requests.get(url).json()

        if not res.get("data") or not res["data"]["results"]:
            return await msg.edit("❌ No results found")

        song = res["data"]["results"][0]

        # 🎵 details
        title = song["name"]
        artist = song["primaryArtists"]
        download_url = song["downloadUrl"][-1]["url"]  # best quality

        file_name = "song.mp3"

        # 🔥 Download audio
        audio_data = requests.get(download_url).content
        with open(file_name, "wb") as f:
            f.write(audio_data)

        await msg.edit("📤 Uploading...")

        # send
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_name,
            caption=f"🎵 {title}\n👤 {artist}",
        )

        os.remove(file_name)
        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Failed to fetch song")
