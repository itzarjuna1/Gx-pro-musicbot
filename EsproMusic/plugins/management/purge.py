import asyncio
import time

from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from EsproMusic import app

async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

@app.on_message(filters.command("purge") & filters.group)
async def purge(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴍᴇssᴀɢᴇ")

    start_time = time.time()
    deleted = 0

    # CASE 1: /purge X
    if len(message.command) > 1 and message.command[1].isdigit():
        count = int(message.command[1])
        start_id = message.reply_to_message.id

        for msg_id in range(start_id, start_id + count):
            try:
                await client.delete_messages(message.chat.id, msg_id)
                deleted += 1
            except:
                pass

    # CASE 2: normal purge
    else:
        start_id = message.reply_to_message.id
        end_id = message.id

        for msg_id in range(start_id, end_id + 1):
            try:
                await client.delete_messages(message.chat.id, msg_id)
                deleted += 1
            except:
                pass

    end_time = time.time()
    taken = round(end_time - start_time, 2)

    # confirmation (auto delete)
    m = await message.reply(
        f"🧹 ᴘᴜʀɢᴇᴅ {deleted} ᴍᴇssᴀɢᴇs\n⏱️ ᴛɪᴍᴇ ᴛᴀᴋᴇɴ: {taken}s"
    )
    await asyncio.sleep(2)
    await m.delete()

@app.on_message(filters.command("spurge") & filters.group)
async def spurge(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return

    if not message.reply_to_message:
        return

    if len(message.command) > 1 and message.command[1].isdigit():
        count = int(message.command[1])
        start_id = message.reply_to_message.id

        for msg_id in range(start_id, start_id + count):
            try:
                await client.delete_messages(message.chat.id, msg_id)
            except:
                pass
    else:
        start_id = message.reply_to_message.id
        end_id = message.id

        for msg_id in range(start_id, end_id + 1):
            try:
                await client.delete_messages(message.chat.id, msg_id)
            except:
                pass


@app.on_message(filters.command("del") & filters.group)
async def delete_msg(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return

    if message.reply_to_message:
        try:
            await message.reply_to_message.delete()
            await message.delete()
        except:
            pass

#file written by @itzarjuna01 © some errors spotted were fixed via ai 
#any marks of ai should be considered as ai fixes 
