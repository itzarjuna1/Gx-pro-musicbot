import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app


@app.on_message(filters.command("music"))
async def yt_music(client: Client, message: Message):
    msg = await message.reply("🔍 Searching on YouTube...")

    if len(message.command) < 2:
        return await msg.edit("Usage: /music song name")

    query = " ".join(message.command[1:])

    try:
        # 🔥 yt-dlp command
        cmd = f'yt-dlp -x --audio-format mp3 --no-playlist "ytsearch1:{query}" -o "%(title)s.%(ext)s"'
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        await process.communicate()

        # 🎵 downloaded file find karna
        file = None
        for f in os.listdir():
            if f.endswith(".mp3"):
                file = f
                break

        if not file:
            return await msg.edit("❌ Download failed")

        await msg.edit("🦋")

        # send
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file,
            caption=f"🎵 {query}",
        )

        # cleanup
        os.remove(file)
        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("❌ Error downloading song")
