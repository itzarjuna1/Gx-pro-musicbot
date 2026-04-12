from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from EsproMusic import app


async def is_admin(client, chat_id, user_id):
    try:
        m = await client.get_chat_member(chat_id, user_id)
        return m.status in [ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER]
    except:
        return False


@app.on_message(filters.command("vcstart") & filters.group)
async def vc_start(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ")

    try:
        await client.create_group_call(message.chat.id)
        await message.reply("🎙️ ᴠᴄ sᴛᴀʀᴛᴇᴅ")
    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ:\n{e}")


@app.on_message(filters.command("vcend") & filters.group)
async def vc_end(client, message: Message):

    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴ ᴏɴʟʏ")

    try:
        chat = await client.get_chat(message.chat.id)

        if not chat.full_info or not chat.full_info.call:
            return await message.reply("❌ ɴᴏ ᴀᴄᴛɪᴠᴇ ᴠᴄ")

        await client.discard_group_call(chat.full_info.call.id)
        await message.reply("🔴 ᴠᴄ ᴇɴᴅᴇᴅ")

    except Exception as e:
        await message.reply(f"❌ ғᴀɪʟᴇᴅ:\n{e}")
