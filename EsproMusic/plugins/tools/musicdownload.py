import os
import requests
import html
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app


@app.on_message(filters.command("music"))
async def music(client, message: Message):
    msg = await message.reply("🦋")

    if len(message.command) < 2:
        return await msg.edit("ᴜsᴀɢᴇ ᴜsᴇ /music (music name) ᴛᴏ sᴇᴀʀᴄʜ ғᴏʀ ᴀɴʏ sᴏɴɢ ᴛᴏ ᴅᴏᴡɴʟᴏᴀᴅ")

    query = " ".join(message.command[1:])

    try:
        # 🔥 YOUR OWN API
        url = f"http://127.0.0.1:3000/api/search/songs?query={query}"
        res = requests.get(url, timeout=10).json()

        if not res.get("data") or not res["data"]["results"]:
            return await msg.edit("❌ No results found")

        song = res["data"]["results"][0]

        # 🎵 Extract info
        title = song["name"]
        artist = song["artists"]["primary"][0]["name"]
        album = song["album"]["name"]
        duration = song["duration"]
        year = song.get("year", "Unknown")
        language = song.get("language", "Unknown")
        audio_url = song["downloadUrl"][-1]["url"]
        thumb_url = song["image"][-1]["url"]

        # 🧹 Clean filename
        file = f"{title.replace('/', '')}.mp4"
        thumb_file = "thumb.jpg"

        await msg.edit("⬇️ ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ᴠɪᴀ sᴇʟғ ʜᴏsᴛᴇᴅ sᴀᴀᴠɴ ᴀᴘɪ")

        # 🔥 Download audio
        audio_data = requests.get(audio_url, timeout=15).content
        with open(file, "wb") as f:
            f.write(audio_data)

        # 🖼 Download thumbnail
        thumb_data = requests.get(thumb_url).content
        with open(thumb_file, "wb") as f:
            f.write(thumb_data)

        await msg.edit("🔍")

        # 🎧 Caption with full info
        caption = f"""<blockquote><b>🎵 {title}
👤 ᴀʀᴛɪsᴛ: {artist}
💿 ᴀʟʙᴜᴍ: {album}
📅 ʏᴇᴀʀ: {year}
🌐 ʟᴀɴɢᴜᴀɢᴇ: {language}
⏱ ᴅᴜʀᴀᴛɪᴏɴ: {duration} sec </b> </blockquote>"""

        # 🚀 Send audio
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file,
            caption=caption,
            thumb=thumb_file,
            parse_mode="html"
        )

        # 🧹 Cleanup
        os.remove(file)
        os.remove(thumb_file)
        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Failed to fetch song")
