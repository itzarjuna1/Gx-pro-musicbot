import asyncio
from pyrogram import Client, filters
from pyrogram.errors import (
    ApiIdInvalid,
    FloodWait,
    PhoneCodeExpired,
    PhoneCodeInvalid,
    PhoneNumberInvalid,
    SessionPasswordNeeded,
    PasswordHashInvalid,
)
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    ApiIdInvalidError,
    PasswordHashInvalidError,
    PhoneCodeExpiredError,
    PhoneCodeInvalidError,
    PhoneNumberInvalidError,
    SessionPasswordNeededError,
)
from telethon.tl.functions.channels import JoinChannelRequest
from pyromod.listen.listen import ListenerTimeout

from config import SUPPORT_CHAT
from EsproString import Loy
from EsproString.utils import retry_key


@Client.on_message(filters.private & filters.command("genstring"))
async def gen_string_cmd(client, message):
    await message.reply_text(
        "» ʜᴇʏ! ᴜsᴇ /start ɪɴ ᴅᴍ ᴛᴏ ɢᴇɴᴇʀᴀᴛᴇ ʏᴏᴜʀ sᴛʀɪɴɢ sᴇssɪᴏɴ.",
        reply_markup=retry_key,
    )


async def gen_session(message, user_id: int, telethon: bool = False):
    if telethon:
        ty = "ᴛᴇʟᴇᴛʜᴏɴ"
    else:
        ty = "ᴩʏʀᴏɢʀᴀᴍ v2"

    await message.reply_text(f"» ᴛʀʏɪɴɢ ᴛᴏ sᴛᴀʀᴛ {ty} sᴇssɪᴏɴ ɢᴇɴᴇʀᴀᴛᴏʀ...")

    try:
        api_id = await Loy.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ɪᴅ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ :",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Loy.send_message(
            user_id,
            "» ᴛɪᴍᴇᴅ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ ᴏғ 5 ᴍɪɴᴜᴛᴇs.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=retry_key,
        )
    if await cancelled(api_id):
        return
    try:
        api_id = int(api_id.text)
    except ValueError:
        return await Loy.send_message(
            user_id,
            "» ᴀᴘɪ ɪᴅ ɪs ɪɴᴠᴀʟɪᴅ.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=retry_key,
        )

    try:
        api_hash = await Loy.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴀᴘɪ ʜᴀsʜ ᴛᴏ ᴘʀᴏᴄᴇᴇᴅ :",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Loy.send_message(
            user_id,
            "» ᴛɪᴍᴇᴅ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ ᴏғ 5 ᴍɪɴᴜᴛᴇs.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=retry_key,
        )
    if await cancelled(api_hash):
        return
    api_hash = api_hash.text

    if len(api_hash) < 30:
        return await Loy.send_message(
            user_id,
            "» ᴀᴘɪ ʜᴀsʜ ɪs ɪɴᴠᴀʟɪᴅ.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=retry_key,
        )

    try:
        phone_number = await Loy.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ :",
            filters=filters.text,
            timeout=300,
        )
    except ListenerTimeout:
        return await Loy.send_message(
            user_id,
            "» ᴛɪᴍᴇᴅ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ ᴏғ 5 ᴍɪɴᴜᴛᴇs.\n\nᴘʟᴇᴀsᴇ ᴛʀʏ ᴀɢᴀɪɴ.",
            reply_markup=retry_key,
        )
    if await cancelled(phone_number):
        return
    phone_number = phone_number.text

    await Loy.send_message(user_id, "» sᴇɴᴅɪɴɢ ᴏᴛᴩ ᴛᴏ ʏᴏᴜʀ ɴᴜᴍʙᴇʀ...")
    client = Client(name="EryxStringGen", api_id=api_id, api_hash=api_hash, in_memory=True)
    await client.connect()

    try:
        code = await client.send_code(phone_number)
        await asyncio.sleep(1)
    except FloodWait as f:
        return await Loy.send_message(
            user_id,
            f"» ғʟᴏᴏᴅ ᴡᴀɪᴛ: ᴘʟᴇᴀsᴇ ᴡᴀɪᴛ {f.value or f.x} sᴇᴄᴏɴᴅs.",
            reply_markup=retry_key,
        )
    except ApiIdInvalid:
        return await Loy.send_message(
            user_id,
            "» ᴀᴘɪ ɪᴅ ᴏʀ ʜᴀsʜ ɪs ɪɴᴠᴀʟɪᴅ.",
            reply_markup=retry_key,
        )
    except PhoneNumberInvalid:
        return await Loy.send_message(
            user_id,
            "» ᴘʜᴏɴᴇ ɴᴜᴍʙᴇʀ ɪɴᴠᴀʟɪᴅ.",
            reply_markup=retry_key,
        )

    try:
        otp = await Loy.ask(
            identifier=(message.chat.id, user_id, None),
            text=f"ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴛʜᴇ ᴏᴛᴩ sᴇɴᴛ ᴛᴏ {phone_number}.",
            filters=filters.text,
            timeout=600,
        )
        if await cancelled(otp):
            return
    except ListenerTimeout:
        return await Loy.send_message(
            user_id,
            "» ᴛɪᴍᴇ ʟɪᴍɪᴛ ʀᴇᴀᴄʜᴇᴅ ᴏғ 10 ᴍɪɴᴜᴛᴇs.",
            reply_markup=retry_key,
        )

    otp = otp.text.replace(" ", "")
    try:
        await client.sign_in(phone_number, code.phone_code_hash, otp)
    except (PhoneCodeInvalid, PhoneCodeExpired):
        return await Loy.send_message(
            user_id,
            "» ᴏᴛᴩ ɪs ᴡʀᴏɴɢ ᴏʀ ᴇxᴩɪʀᴇᴅ.",
            reply_markup=retry_key,
        )
    except SessionPasswordNeeded:
        pwd = await Loy.ask(
            identifier=(message.chat.id, user_id, None),
            text="» ᴇɴᴛᴇʀ ʏᴏᴜʀ ᴛᴡᴏ sᴛᴇᴘ ᴘᴀssᴡᴏʀᴅ :",
            filters=filters.text,
            timeout=300,
        )
        await client.check_password(password=pwd.text)

    string_session = await client.export_session_string()
    txt = (
        f"ʜᴇʀᴇ ɪs ʏᴏᴜʀ {ty} sᴛʀɪɴɢ sᴇssɪᴏɴ\n\n"
        f"<code>{string_session}</code>\n\n"
        f"ᴀ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛᴏʀ ʙᴏᴛ ʙʏ <a href={SUPPORT_CHAT}>ᴇʀʏx sᴜᴘᴘᴏʀᴛ</a>"
    )
    await client.send_message("me", txt, disable_web_page_preview=True, parse_mode="html")
    await client.join_chat("EsproUpdate")
    await client.disconnect()

    await Loy.send_message(
        chat_id=user_id,
        text=f"sᴜᴄᴄᴇssғᴜʟʟʏ ɢᴇɴᴇʀᴀᴛᴇᴅ ʏᴏᴜʀ {ty} sᴛʀɪɴɢ sᴇssɪᴏɴ.\n\nᴄʜᴇᴄᴋ ʏᴏᴜʀ sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="sᴀᴠᴇᴅ ᴍᴇssᴀɢᴇs",
                        url=f"tg://openmessage?user_id={user_id}",
                    )
                ]
            ]
        ),
    )


async def cancelled(message):
    if "/cancel" in message.text:
        await message.reply_text(
            "» ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜᴇ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛɪᴏɴ.", reply_markup=retry_key
        )
        return True
    elif message.text.startswith("/"):
        await message.reply_text(
            "» ᴄᴀɴᴄᴇʟʟᴇᴅ ᴛʜᴇ sᴛʀɪɴɢ ɢᴇɴᴇʀᴀᴛɪᴏɴ.", reply_markup=retry_key
        )
        return True
    return False
