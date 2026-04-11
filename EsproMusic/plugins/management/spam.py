# ================== SPAM SYSTEM ==================

import asyncio
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app
from config import OWNER_ID

# ================== STATE ==================
SPAM_TASKS = {}


# ================== SPAM ==================
@app.on_message(filters.command("spam") & filters.group)
async def spam_cmd(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    if len(message.command) < 4:
        return await message.reply_text(
            "ᴜsᴀɢᴇ:\n/spam <count> <speed> <message>"
        )

    try:
        count = int(message.command[1])
        speed = float(message.command[2])
        text = message.text.split(None, 3)[3]
    except:
        return await message.reply_text("ɪɴᴠᴀʟɪᴅ ғᴏʀᴍᴀᴛ")

    if speed <= 0:
        return await message.reply_text("sᴘᴇᴇᴅ ᴍᴜsᴛ ʙᴇ > 0")

    delay = 1 / speed
    chat_id = message.chat.id

    # stop old spam if exists
    if chat_id in SPAM_TASKS:
        SPAM_TASKS[chat_id].cancel()

    async def spam_loop():
        try:
            for _ in range(count):
                await client.send_message(chat_id, text)
                await asyncio.sleep(delay)
        except asyncio.CancelledError:
            pass

    task = asyncio.create_task(spam_loop())
    SPAM_TASKS[chat_id] = task

    await message.reply_text(
        f"🚀 sᴘᴀᴍ sᴛᴀʀᴛᴇᴅ\n"
        f"• ᴄᴏᴜɴᴛ: {count}\n"
        f"• sᴘᴇᴇᴅ: {speed} msg/sec"
    )


# ================== STOP ==================
@app.on_message(filters.command("stopspam") & filters.group)
async def stop_spam(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return

    chat_id = message.chat.id

    if chat_id not in SPAM_TASKS:
        return await message.reply_text("ɴᴏ sᴘᴀᴍ ʀᴜɴɴɪɴɢ")

    SPAM_TASKS[chat_id].cancel()
    del SPAM_TASKS[chat_id]

    await message.reply_text("🛑 sᴘᴀᴍ sᴛᴏᴘᴘᴇᴅ")
