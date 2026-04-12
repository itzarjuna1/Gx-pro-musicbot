import os
import random
import string

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from pyrogram.enums import ButtonStyle
from PIL import Image, ImageFilter

from EsproMusic import app


TEMP = "stickers"
os.makedirs(TEMP, exist_ok=True)

album_cache = {}
pending = {}


def rnd():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))


def resize(inp):
    img = Image.open(inp).convert("RGBA")
    img.thumbnail((512, 512))
    out = inp + ".webp"
    img.save(out, "WEBP")
    return out


def effect_glow(path):
    img = Image.open(path).convert("RGBA")
    glow = img.filter(ImageFilter.GaussianBlur(8))
    out = path + "_glow.webp"
    glow.save(out, "WEBP")
    return out


def effect_outline(path):
    img = Image.open(path).convert("RGBA")
    edge = img.filter(ImageFilter.FIND_EDGES)
    out = path + "_edge.webp"
    edge.save(out, "WEBP")
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

    pending[m.from_user.id] = {
        "mode": mode,
        "chat": m.chat.id,
        "msg_id": m.reply_to_message.id,
        "emoji": emoji
    }

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("ʏᴇs", callback_data="confirm_yes", style=ButtonStyle.SUCCESS),
            InlineKeyboardButton("ɴᴏ", callback_data="confirm_no", style=ButtonStyle.DANGER)
        ]
    ])

    await m.reply("ᴄᴏɴғɪʀᴍ ɢᴇɴᴇʀᴀᴛɪᴏɴ?", reply_markup=kb)


@app.on_callback_query()
async def confirm(_, q: CallbackQuery):

    user = q.from_user.id

    if user not in pending:
        return await q.answer("ᴇxᴘɪʀᴇᴅ", True)

    if q.data == "confirm_no":
        pending.pop(user, None)
        return await q.message.edit("ᴄᴀɴᴄᴇʟʟᴇᴅ")

    data = pending.pop(user)
    mode = data["mode"]
    emoji = data["emoji"]

    msg = await app.get_messages(data["chat"], data["msg_id"])

    if mode == "sticker":

        if not (msg.photo or msg.document):
            return await q.message.reply("ɪɴᴠᴀʟɪᴅ")

        file = await msg.download(f"{TEMP}/{rnd()}")
        webp = resize(file)

        webp = random.choice([webp, effect_glow(webp), effect_outline(webp)])

        await q.message.reply_sticker(webp)

        os.remove(file)


    elif mode == "stickerpack":

        if not msg.media_group_id:
            return await q.message.reply("ɴᴏ ᴀʟʙᴜᴍ")

        media = album_cache.get(msg.media_group_id)

        if not media:
            return await q.message.reply("ᴀʟʙᴜᴍ ɴᴏᴛ ᴄᴀᴄʜᴇᴅ")

        name = await pack_name(q.from_user)
        title = f"{q.from_user.first_name}'s pack"

        first = True

        for m in media:

            if not (m.photo or m.document):
                continue

            file = await m.download(f"{TEMP}/{rnd()}")
            webp = resize(file)

            try:
                if first:
                    await app.create_new_sticker_set(
                        user_id=q.from_user.id,
                        name=name,
                        title=title,
                        stickers=[webp],
                        emojis=emoji
                    )
                    first = False
                else:
                    await app.add_sticker_to_set(
                        user_id=q.from_user.id,
                        name=name,
                        sticker=webp,
                        emojis=emoji
                    )
            except Exception as e:
                print(e)

            os.remove(file)
            os.remove(webp)

        await q.message.reply(f"https://t.me/addstickers/{name}")


    elif mode == "emoji":

        if not (msg.photo or msg.document):
            return await q.message.reply("ɪɴᴠᴀʟɪᴅ")

        file = await msg.download(f"{TEMP}/{rnd()}")
        webp = resize(file)

        name = await pack_name(q.from_user)

        await app.create_new_sticker_set(
            user_id=q.from_user.id,
            name=name,
            title="custom emoji",
            stickers=[webp],
            emojis=emoji
        )

        await q.message.reply(f"https://t.me/addstickers/{name}")
