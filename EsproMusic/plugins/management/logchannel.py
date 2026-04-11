#file written by @itzarjuna01 © some errors spotted were fixed via ai 
#any marks of ai should be considered as ai fixes 
from datetime import datetime
from functools import wraps
from pyrogram import filters

from pyrogram import Client
from pyrogram.types import Message
from pyrogram.errors import ChatAdminRequired, RPCError

from EsproMusic import app
from EsproMusic.core.mongo import log_db  # 👈 create this collection in mongo file

# ================== MONGO HELPERS ==================

def get_log(chat_id: int):
    data = log_db.find_one({"chat_id": chat_id})
    return data["log_chat"] if data else None


def set_log(chat_id: int, log_chat_id: int):
    log_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"log_chat": log_chat_id}},
        upsert=True
    )


def unset_log(chat_id: int):
    log_db.delete_one({"chat_id": chat_id})


# ================== LOG DECORATOR ==================

def loggable(func):
    @wraps(func)
    async def wrapper(client: Client, message: Message, *args, **kwargs):

        result = await func(client, message, *args, **kwargs)

        if not result:
            return result

        chat = message.chat

        stamp = datetime.utcnow().strftime("%H:%M - %d/%m/%Y")

        log_text = (
            f"💮 𝗘𝗩𝗘𝗡𝗧 𝗟𝗢𝗚 💮\n\n"
            f"{result}\n\n"
            f"🕒 𝘀𝘁𝗮𝗺𝗽: {stamp}\n"
            f"💬 𝗰𝗵𝗮𝘁: {chat.title or chat.id}"
        )

        log_chat = get_log(chat.id)

        if log_chat:
            try:
                await client.send_message(
                    log_chat,
                    log_text,
                    disable_web_page_preview=True
                )
            except RPCError:
                pass

        return result

    return wrapper


# ================== COMMANDS ==================

@app.on_message(filters.command("logchannel") & filters.group)
async def get_log_channel(client, message: Message):
    log_chat = get_log(message.chat.id)

    if not log_chat:
        return await message.reply("💮 ɴᴏ ʟᴏɢ ᴄʜᴀɴɴᴇʟ sᴇᴛ ʏᴇᴛ")

    try:
        chat = await client.get_chat(log_chat)
        name = chat.title
    except:
        name = "Unknown"

    await message.reply(
        f"💮 ʟᴏɢ ᴄʜᴀɴɴᴇʟ:\n"
        f"➥ {name}\n"
        f"➥ `{log_chat}`"
    )


@app.on_message(filters.command("setlog") & filters.group)
async def set_log_channel(client, message: Message):

    if not message.reply_to_message:
        return await message.reply("💮 ʀᴇᴘʟʏ ᴛᴏ ᴀ ᴄʜᴀɴɴᴇʟ ᴍᴇssᴀɢᴇ")

    try:
        channel_id = message.reply_to_message.forward_from_chat.id
    except:
        return await message.reply("💮 ɪɴᴠᴀʟɪᴅ ᴄʜᴀɴɴᴇʟ")

    set_log(message.chat.id, channel_id)

    await message.reply(
        "💮 ʟᴏɢ ᴄʜᴀɴɴᴇʟ sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ ✨"
    )


@app.on_message(filters.command("unsetlog") & filters.group)
async def unset_log_channel(client, message: Message):

    unset_log(message.chat.id)

    await message.reply(
        "💮 ʟᴏɢ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇᴅ ✨"
  )
