import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from oldpyro import Client as Client1

from telethon import TelegramClient
from telethon.sessions import StringSession

from EsproMusic import app


# ─────────────────────────────────────────────
# ʀᴇsᴛʀɪᴄᴛ ɢʀᴏᴜᴘ ᴜsᴀɢᴇ
# ─────────────────────────────────────────────
async def not_private(message: Message):
    return await message.reply_text(
        "» ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴍᴇ ɪɴ ᴅᴍ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ sᴛʀɪɴɢ sᴇssɪᴏɴ.\n\n"
        "☠ ᴜsᴇ /genstring ɪɴ ᴘʀɪᴠᴀᴛᴇ."
    )


# ─────────────────────────────────────────────
# sᴛᴀʀᴛ ᴄᴏᴍᴍᴀɴᴅ
# ─────────────────────────────────────────────
@app.on_message(filters.command("genstring") & ~filters.private)
async def genstring_group(_, message: Message):
    return await not_private(message)


@app.on_message(filters.command("genstring") & filters.private)
async def genstring_home(_, message: Message):
    await message.reply_text(
        "˹ᴇʀʏx ꭙ sᴛʀɪɴɢ ɢᴇɴ˼ ♪\n\n"
        "» ᴄʜᴏᴏsᴇ sᴇssɪᴏɴ ᴛʏᴘᴇ :\n\n"
        "• /pyro  → ᴩʏʀᴏɢʀᴀᴍ v2\n"
        "• /tele  → ᴛᴇʟᴇᴛʜᴏɴ\n"
        "• /pyro1 → ᴩʏʀᴏɢʀᴀᴍ v1\n\n"
        "☠ ɢᴇɴᴇʀᴀᴛᴇ ɪɴ ᴩʀɪᴠᴀᴛᴇ ᴏɴʟʏ."
    )


# ─────────────────────────────────────────────
# ᴄᴏʀᴇ ʟᴏɢɪᴄ
# ─────────────────────────────────────────────
async def gen_session(message, user_id: int, telethon=False, old_pyro=False):
    if telethon:
        ty = "ᴛᴇʟᴇᴛʜᴏɴ"
    elif old_pyro:
        ty = "ᴩʏʀᴏɢʀᴀᴍ v1"
    else:
        ty = "ᴩʏʀᴏɢʀᴀᴍ v2"

    await message.reply_text(f"» sᴛᴀʀᴛɪɴɢ {ty} sᴇssɪᴏɴ...")

    try:
        api_id = await app.ask(message.chat.id, "» ᴇɴᴛᴇʀ ᴀᴘɪ ɪᴅ :", timeout=300)
        api_id = int(api_id.text)
    except:
        return await message.reply_text("» ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ɪᴅ.")

    try:
        api_hash = await app.ask(message.chat.id, "» ᴇɴᴛᴇʀ ᴀᴘɪ ʜᴀsʜ :", timeout=300)
        api_hash = api_hash.text
    except:
        return await message.reply_text("» ɪɴᴠᴀʟɪᴅ ᴀᴘɪ ʜᴀsʜ.")

    try:
        phone = await app.ask(message.chat.id, "» ᴇɴᴛᴇʀ ᴘʜᴏɴᴇ (+91...):", timeout=300)
        phone = phone.text
    except:
        return await message.reply_text("» ɪɴᴠᴀʟɪᴅ ɴᴜᴍʙᴇʀ.")

    await message.reply_text("» sᴇɴᴅɪɴɢ ᴏᴛᴘ...")

    if telethon:
        client = TelegramClient(StringSession(), api_id, api_hash)
    elif old_pyro:
        client = Client1(":memory:", api_id=api_id, api_hash=api_hash)
    else:
        client = Client(name="eryx", api_id=api_id, api_hash=api_hash, in_memory=True)

    await client.connect()

    try:
        if telethon:
            code = await client.send_code_request(phone)
        else:
            code = await client.send_code(phone)
    except Exception as e:
        return await message.reply_text(f"» ᴇʀʀᴏʀ : {e}")

    try:
        otp = await app.ask(message.chat.id, "» ᴇɴᴛᴇʀ ᴏᴛᴘ :", timeout=600)
        otp = otp.text.replace(" ", "")
    except:
        return await message.reply_text("» ᴏᴛᴘ ᴛɪᴍᴇᴏᴜᴛ.")

    try:
        if telethon:
            await client.sign_in(phone, otp)
        else:
            await client.sign_in(phone, code.phone_code_hash, otp)
    except Exception as e:
        return await message.reply_text(f"» ʟᴏɢɪɴ ғᴀɪʟᴇᴅ : {e}")

    try:
        if telethon:
            string = client.session.save()
        else:
            string = await client.export_session_string()

        await client.send_message(
            "me",
            f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ {ty} sᴛʀɪɴɢ sᴇssɪᴏɴ\n\n<code>{string}</code>",
            parse_mode="html",
        )
    except:
        pass

    await client.disconnect()

    await message.reply_text(
        "» sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ.\n\nᴄʜᴇᴄᴋ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs."
    )


# ─────────────────────────────────────────────
# ᴄᴏᴍᴍᴀɴᴅs (ᴅᴍ ᴏɴʟʏ)
# ─────────────────────────────────────────────
@app.on_message(filters.command("pyro") & ~filters.private)
async def pyro_group(_, message: Message):
    return await not_private(message)


@app.on_message(filters.command("tele") & ~filters.private)
async def tele_group(_, message: Message):
    return await not_private(message)


@app.on_message(filters.command("pyro1") & ~filters.private)
async def pyro1_group(_, message: Message):
    return await not_private(message)


@app.on_message(filters.command("pyro") & filters.private)
async def pyro(_, message: Message):
    await gen_session(message, message.from_user.id)


@app.on_message(filters.command("tele") & filters.private)
async def tele(_, message: Message):
    await gen_session(message, message.from_user.id, telethon=True)


@app.on_message(filters.command("pyro1") & filters.private)
async def pyro1(_, message: Message):
    await gen_session(message, message.from_user.id, old_pyro=True)
