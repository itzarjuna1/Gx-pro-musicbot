from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatType

from EsproMusic import app


@app.on_message(filters.command("ginfo") & filters.group)
async def groupinfo_handler(client, message: Message):

    chat = message.chat

    if chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        return await message.reply(
            "❌ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏʀᴋs ᴏɴʟʏ ɪɴ ɢʀᴏᴜᴘs"
        )

    try:
        title = chat.title
        gid = chat.id
        username = f"@{chat.username}" if chat.username else "ɴᴏ ᴜsᴇʀɴᴀᴍᴇ"
        desc = chat.description or "ɴᴏ ᴅᴇsᴄʀɪᴘᴛɪᴏɴ"

        members = await client.get_chat_members_count(gid)

        text = (
            "👥 ɢʀᴏᴜᴘ ɪɴғᴏ\n\n"
            f"🏷 ᴛɪᴛʟᴇ: {title}\n"
            f"🆔 ɪᴅ: `{gid}`\n"
            f"🔗 ᴜsᴇʀɴᴀᴍᴇ: {username}\n"
            f"👤 ᴍᴇᴍʙᴇʀs: `{members}`\n\n"
            f"📝 ᴅᴇsᴄʀɪᴘᴛɪᴏɴ:\n{desc}"
        )

        await message.reply(
            text,
            disable_web_page_preview=True
        )

    except Exception as e:
        await message.reply(f"❌ ᴇʀʀᴏʀ: {e}")
