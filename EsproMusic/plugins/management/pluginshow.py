import os

from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app
from config import OWNER_ID


BASE = "EsproMusic/plugins"


def is_owner(uid):
    if isinstance(OWNER_ID, list):
        return uid in OWNER_ID
    return uid == OWNER_ID


def fmt(x):
    return x.replace("_", " ").lower()


@app.on_message(filters.command("plugins"))
async def plugins(_, m: Message):

    if not is_owner(m.from_user.id):
        return

    if not os.path.exists(BASE):
        return await m.reply("ɴᴏ ᴘʟᴜɢɪɴs ғᴏᴜɴᴅ")

    text = "✦ ᴘʟᴜɢɪɴ ʟɪsᴛ ✦\n\n"

    folders = sorted(os.listdir(BASE))

    for folder in folders:

        path = os.path.join(BASE, folder)

        if not os.path.isdir(path):
            continue

        files = [
            f for f in os.listdir(path)
            if f.endswith(".py") and not f.startswith("_")
        ]

        if not files:
            continue

        text += f"❖ {fmt(folder)}\n"

        for f in sorted(files):
            name = f.replace(".py", "")
            text += f"   • {fmt(name)}\n"

        text += "\n"

    text += "— powered by @theinfinitynetwork"

    await m.reply(text)
