import os
import random
import string

from pyrogram import filters
from pyrogram.types import Message
from PIL import Image

from EsproMusic import app


TEMP = "stickers"
os.makedirs(TEMP, exist_ok=True)

album_cache = {}


def rnd():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def resize(inp):
    img = Image.open(inp).convert("RGBA")
    img.thumbnail((512, 512))
    out = inp + ".webp"
    img.save(out, "WEBP")
    return out


async def pack_name(user):
    bot = await app.get_me()
    return f"{user.first_name.lower()}_{rnd()}_by_{bot.username}"


@app.on_message(filters.group & filters.media_group)
async def cache_album(_, m: Message):
    album_cache.setdefault(m.media_group_id, []).append(m)


@app.on_message(filters.command("generate") & filters.reply)
async def generate(_, m: Message):

    if len(m.command) < 2:
        return await m.reply("ᴜsᴇ ➜ /generate sticker | stickerpack | emoji 😎")

    mode = m.command[1].lower()
    emoji = m.command[2] if len(m.command) > 2 else "🔥"

    msg = m.reply_to_message


    if mode == "sticker":

        if not (msg.photo or msg.document):
            return await m.reply("ɪɴᴠᴀʟɪᴅ ᴍᴇᴅɪᴀ")

        file = await msg.download(f"{TEMP}/{rnd()}")
        webp = resize(file)

        await m.reply_sticker(webp)

        os.remove(file)
        os.remove(webp)


    elif mode == "stickerpack":

        if not msg.media_group_id:
            return await m.reply("ʀᴇᴘʟʏ ᴛᴏ ᴀɴ ᴀʟʙᴜᴍ")

        media = album_cache.get(msg.media_group_id)

        if not media:
            return await m.reply("ᴀʟʙᴜᴍ ɴᴏᴛ ᴄᴀᴄʜᴇᴅ")

        name = await pack_name(m.from_user)
        title = f"{m.from_user.first_name}'s pack"

        first = True

        for x in media:

            if not (x.photo or x.document):
                continue

            file = await x.download(f"{TEMP}/{rnd()}")
            webp = resize(file)

            try:
                if first:
                    await app.create_new_sticker_set(
                        user_id=m.from_user.id,
                        name=name,
                        title=title,
                        stickers=[webp],
                        emojis=emoji
                    )
                    first = False
                else:
                    await app.add_sticker_to_set(
                        user_id=m.from_user.id,
                        name=name,
                        sticker=webp,
                        emojis=emoji
                    )
            except Exception as e:
                print(e)

            os.remove(file)
            os.remove(webp)

        await m.reply(f"https://t.me/addstickers/{name}")


    elif mode == "emoji":

        if not (msg.photo or msg.document):
            return await m.reply("ɪɴᴠᴀʟɪᴅ")

        file = await msg.download(f"{TEMP}/{rnd()}")
        webp = resize(file)

        name = await pack_name(m.from_user)

        await app.create_new_sticker_set(
            user_id=m.from_user.id,
            name=name,
            title="custom emoji",
            stickers=[webp],
            emojis=emoji
        )

        await m.reply(f"https://t.me/addstickers/{name}")
