import os
import asyncio
import random
import string

from pyrogram import filters
from pyrogram.types import Message
from PIL import Image

from EsproMusic import app


TEMP_DIR = "stickers"
os.makedirs(TEMP_DIR, exist_ok=True)


def rand():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def resize(path):
    img = Image.open(path)
    img.thumbnail((512, 512))
    out = path + ".webp"
    img.save(out, "WEBP")
    return out


async def make_pack_name(user):
    base = user.first_name.lower().replace(" ", "")
    return f"{base}_{rand()}_by_{(await app.get_me()).username}"


@app.on_message(filters.command("generate") & filters.reply)
async def generate(client, message: Message):

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➜ /generate sticker OR stickerpack")

    mode = message.command[1].lower()
    reply = message.reply_to_message

    if mode == "sticker":

        if not (reply.photo or reply.video or reply.document):
            return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ɪᴍᴀɢᴇ/ᴠɪᴅᴇᴏ")

        file = await reply.download(file_name=f"{TEMP_DIR}/{rand()}")

        webp = resize(file)

        await message.reply_sticker(webp)

        return os.remove(file)

    elif mode == "stickerpack":

        if not reply.media_group_id:
            return await message.reply("❌ ʀᴇᴘʟʏ ᴛᴏ ᴀʟʙᴜᴍ")

        media = []

        async for msg in app.get_chat_history(
            message.chat.id,
            limit=20
        ):
            if msg.media_group_id == reply.media_group_id:
                media.append(msg)

        media.reverse()

        if not media:
            return await message.reply("❌ ɴᴏ ᴍᴇᴅɪᴀ")

        user = message.from_user
        pack_name = await make_pack_name(user)
        pack_title = f"{user.first_name}'s pack"

        first = True

        for m in media:

            if not (m.photo or m.document):
                continue

            file = await m.download(file_name=f"{TEMP_DIR}/{rand()}")
            webp = resize(file)

            try:
                if first:
                    await app.create_new_sticker_set(
                        user_id=user.id,
                        name=pack_name,
                        title=pack_title,
                        stickers=[webp],
                        emojis="🔥"
                    )
                    first = False
                else:
                    await app.add_sticker_to_set(
                        user_id=user.id,
                        name=pack_name,
                        sticker=webp,
                        emojis="🔥"
                    )
            except Exception as e:
                print(e)

            os.remove(file)
            os.remove(webp)

        link = f"https://t.me/addstickers/{pack_name}"

        await message.reply(f"✅ ᴘᴀᴄᴋ ʀᴇᴀᴅʏ:\n{link}")
