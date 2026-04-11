# ================== USER NETWORK CHECK (SIMULATED) ==================

import time
import asyncio

from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app


# ================== COMMAND ==================
@app.on_message(filters.command("checkmynet"))
async def check_net(client, message: Message):

    start = time.time()

    msg = await message.reply("📡 ᴄʜᴇᴄᴋɪɴɢ ʏᴏᴜʀ ɴᴇᴛᴡᴏʀᴋ...")

    # simulate delay check
    await asyncio.sleep(1.5)

    end = time.time()
    latency = round((end - start) * 1000)

    # ===== CLASSIFY =====
    if latency < 600:
        status = "🟢 ᴇxᴄᴇʟʟᴇɴᴛ"
    elif latency < 1200:
        status = "🟡 ɴᴏʀᴍᴀʟ"
    else:
        status = "🔴 ʟᴀɢɢʏ"

    await msg.edit(
        f"📡 **ɴᴇᴛᴡᴏʀᴋ ᴀɴᴀʟʏsɪs**\n\n"
        f"⏱ ʀᴇsᴘᴏɴsᴇ: `{latency} ms`\n"
        f"📶 sᴛᴀᴛᴜs: {status}\n\n"
        f"⚠️ ɴᴏᴛᴇ: ᴛʜɪs ɪs ᴀ sɪᴍᴜʟᴀᴛᴇᴅ ᴇsᴛɪᴍᴀᴛᴇ"
    )
