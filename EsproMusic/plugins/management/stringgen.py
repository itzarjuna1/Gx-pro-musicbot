import asyncio
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

try:
    from pyrogram.enums import ButtonStyle
    SUPPORT_STYLE = True
except:
    SUPPORT_STYLE = False

from pyrogram.errors import SessionPasswordNeeded
from pyrogram import Client as PyroClient
from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from EsproMusic import app
from config import API_ID, API_HASH

PRIVACY_LINK = "https://telegra.ph/Your-Privacy-Policy-Here"

users = {}

def btn(text, **kwargs):
    if SUPPORT_STYLE and "style" in kwargs:
        style = kwargs.pop("style")
        return InlineKeyboardButton(text, **kwargs, style=style)
    return InlineKeyboardButton(text, **kwargs)

@app.on_message(filters.command("gensession") & filters.group)
async def group_redirect(client, message: Message):
    bot_username = (await client.get_me()).username
    await message.reply(
        "⚠️ ᴘʟᴇᴀsᴇ ᴜsᴇ ɪɴ ᴅᴍ",
        reply_markup=InlineKeyboardMarkup([
            [
                btn(
                    "🚀 sᴛᴀʀᴛ ᴍᴇ",
                    url=f"https://t.me/{bot_username}?start=gensession",
                    style=ButtonStyle.PRIMARY if SUPPORT_STYLE else None
                )
            ]
        ])
    )

@app.on_message(filters.command("gensession") & filters.private)
async def start_dm(client, message: Message):
    await message.reply(
        "╭─〔 ⚙️ sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ 〕─╮\n│ ✦ sᴇʟᴇᴄᴛ sᴇssɪᴏɴ ᴛʏᴘᴇ\n│ ✦ ᴋᴇᴇᴘ ɪᴛ sᴇᴄʀᴇᴛ\n╰────────────────╯",
        reply_markup=InlineKeyboardMarkup([
            [
                btn("🐍 ᴘʏʀᴏɢʀᴀᴍ", callback_data="pyro", style=ButtonStyle.SUCCESS if SUPPORT_STYLE else None),
                btn("📡 ᴛᴇʟᴇᴛʜᴏɴ", callback_data="tele", style=ButtonStyle.PRIMARY if SUPPORT_STYLE else None)
            ],
            [
                btn("🔐 ᴘʀɪᴠᴀᴄʏ", url=PRIVACY_LINK, style=ButtonStyle.SUCCESS if SUPPORT_STYLE else None)
            ],
            [
                btn("❌ ᴄʟᴏsᴇ", callback_data="close", style=ButtonStyle.DANGER if SUPPORT_STYLE else None)
            ]
        ])
    )

@app.on_callback_query(filters.regex("^(pyro|tele|close)$"))
async def callbacks(client, query):
    user_id = query.from_user.id

    if query.data == "close":
        return await query.message.delete()

    if query.data in ["pyro", "tele"]:
        users[user_id] = {"type": query.data}
        await query.message.reply("📱 sᴇɴᴅ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ\n\nᴇxᴀᴍᴘʟᴇ: +911234567890")

@app.on_message(filters.private & filters.text & ~filters.command(["gensession"]))
async def session_flow(client, message: Message):
    user_id = message.from_user.id

    if user_id not in users:
        return

    data = users[user_id]

    if "phone" not in data:
        data["phone"] = message.text

        try:
            if data["type"] == "pyro":
                client_ = PyroClient(f"user_{user_id}", api_id=API_ID, api_hash=API_HASH)
                await client_.connect()
                sent = await client_.send_code(data["phone"])
                data["client"] = client_
                data["hash"] = sent.phone_code_hash
            else:
                client_ = TelegramClient(StringSession(), API_ID, API_HASH)
                await client_.connect()
                sent = await client_.send_code_request(data["phone"])
                data["client"] = client_
                data["hash"] = sent.phone_code_hash

            await message.reply("🔐 ᴇɴᴛᴇʀ ᴏᴛᴘ")

        except Exception as e:
            users.pop(user_id, None)
            await message.reply(f"❌ ᴇʀʀᴏʀ:\n{e}")

    elif "otp" not in data:
        data["otp"] = message.text.replace(" ", "")

        try:
            if data["type"] == "pyro":
                await data["client"].sign_in(data["phone"], data["hash"], data["otp"])
            else:
                await data["client"].sign_in(data["phone"], data["otp"])

            try:
                string = await data["client"].export_session_string()
            except:
                string = data["client"].session.save()

            await message.reply(f"✅ sᴇssɪᴏɴ:\n\n`{string}`")

            await data["client"].disconnect()
            users.pop(user_id, None)

        except SessionPasswordNeeded:
            data["2fa"] = True
            await message.reply("🔑 sᴇɴᴅ 2ғᴀ ᴘᴀssᴡᴏʀᴅ")

        except Exception as e:
            users.pop(user_id, None)
            await message.reply(f"❌ ᴇʀʀᴏʀ:\n{e}")

    elif data.get("2fa"):
        try:
            await data["client"].check_password(message.text)

            try:
                string = await data["client"].export_session_string()
            except:
                string = data["client"].session.save()

            await message.reply(f"✅ sᴇssɪᴏɴ:\n\n`{string}`")

            await data["client"].disconnect()
            users.pop(user_id, None)

        except Exception as e:
            users.pop(user_id, None)
            await message.reply(f"❌ ᴇʀʀᴏʀ:\n{e}")
