import os
import requests
import asyncio
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app

# 🔥 loading animation
async def loading(msg):
    frames = ["🔍 sᴇᴀʀᴄʜɪɴɢ.", "🔍 sᴇᴀʀᴄʜɪɴɢ..", "🔍 sᴇᴀʀᴄʜɪɴɢ..."]
    for _ in range(2):
        for frame in frames:
            await msg.edit(frame)
            await asyncio.sleep(0.5)


@app.on_message(filters.command("music"))
async def music(client, message: Message):
    msg = await message.reply("🔍 sᴇᴀʀᴄʜɪɴɢ...")

    if len(message.command) < 2:
        return await msg.edit("❌ ᴜsᴀɢᴇ: /music sᴏɴɢ ɴᴀᴍᴇ")

    query = " ".join(message.command[1:])

    try:
        await loading(msg)

        # 🔥 YOUR API
        url = f"http://127.0.0.1:3000/api/search/songs?query={query}"
        res = requests.get(url, timeout=10).json()

        if not res.get("data") or not res["data"]["results"]:
            return await msg.edit("❌ ɴᴏ ʀᴇsᴜʟᴛs ғᴏᴜɴᴅ")

        song = res["data"]["results"][0]

        # 🎵 data
        title = song["name"]
        artist = song["artists"]["primary"][0]["name"]
        album = song["album"]["name"]
        year = song.get("year", "unknown")
        language = song.get("language", "unknown")
        duration = song["duration"]

        audio_url = song["downloadUrl"][-1]["url"]
        thumb_url = song["image"][-1]["url"]

        file = f"{title.replace('/', '')}.mp4"
        thumb_file = "thumb.jpg"

        await msg.edit("⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...")

        # 🎧 download audio
        audio_data = requests.get(audio_url, timeout=15).content
        with open(file, "wb") as f:
            f.write(audio_data)

        # 🖼 download thumbnail
        thumb_data = requests.get(thumb_url).content
        with open(thumb_file, "wb") as f:
            f.write(thumb_data)

        # 🖼 SEND IMAGE BEFORE SONG
        IMAGE_URL = "https://files.catbox.moe/8fdj9b.jpg"  # 🔁 replace

        await client.send_photo(
            chat_id=message.chat.id,
            photo=IMAGE_URL,
            caption="🎧 sᴏɴɢ ɪs ᴄᴏᴍɪɴɢ..."
        )

        await msg.edit("📤 ᴜᴘʟᴏᴀᴅɪɴɢ...")

        # 🎧 caption
        caption = f"""╭───『 🎵 sᴏɴɢ ɪɴғᴏ 』───╮
│
│ 🎶 {title}
│ 👤 {artist}
│ 💿 {album}
│ 📅 {year}
│ 🌐 {language}
│ ⏱ {duration} sᴇᴄ
│
╰────────────────────╯"""

        # 🚀 send audio
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file,
            caption=caption,
            thumb=thumb_file
        )

        # 🧹 cleanup
        os.remove(file)
        os.remove(thumb_file)
        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ ғᴀɪʟᴇᴅ")
