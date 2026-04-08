import os
import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app


@app.on_message(filters.command("music"))
async def yt_music(client: Client, message: Message):
    msg = await message.reply("🦋")

    if len(message.command) < 2:
        return await msg.edit("Usage: /music song name")

    query = " ".join(message.command[1:])

    try:
        file_name = "song.mp3"

        cmd = [
            "yt-dlp",
            "-x",
            "--audio-format", "mp3",
            "--ffmpeg-location", "/usr/bin/ffmpeg",
            "-o", file_name,
            f"ytsearch1:{query}"
        ]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            print(stderr.decode())
            return await msg.edit("❌ Download failed")

        if not os.path.exists(file_name):
            return await msg.edit("❌ File not found")

        await msg.edit("📤 Uploading...")

        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_name,
            caption=f"🎵 {query}",
        )

        os.remove(file_name)
        await msg.delete()

    except Exception as e:
        print("ERROR:", e)
        await msg.edit("❌ Error downloading song")
