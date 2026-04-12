import os

from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from EsproMusic import app
from config import OWNER_ID


BASE = "EsproMusic/plugins"


def is_owner(uid):
    if isinstance(OWNER_ID, list):
        return uid in OWNER_ID
    return uid == OWNER_ID


def fmt(x):
    return x.replace("_", " ").title()


def get_folders():
    return [
        f for f in os.listdir(BASE)
        if os.path.isdir(os.path.join(BASE, f))
    ]


def get_files(folder):
    path = os.path.join(BASE, folder)

    if not os.path.exists(path):
        return []

    return [
        f.replace(".py", "")
        for f in os.listdir(path)
        if f.endswith(".py") and not f.startswith("_")
    ]


@app.on_message(filters.command("plugins"))
async def plugins(_, m: Message):

    if not is_owner(m.from_user.id):
        return

    folders = get_folders()

    if not folders:
        return await m.reply("ɴᴏ ᴘʟᴜɢɪɴs")

    buttons = [
        [InlineKeyboardButton(fmt(f), callback_data=f"plug|{f}")]
        for f in folders
    ]

    buttons.append([
        InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="plug|close")
    ])

    await m.reply(
        "✦ ᴘʟᴜɢɪɴ ᴘᴀɴᴇʟ ✦\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ",
        reply_markup=InlineKeyboardMarkup(buttons)
    )


@app.on_callback_query(filters.regex("^plug\\|"))
async def panel(_, q: CallbackQuery):

    if not is_owner(q.from_user.id):
        return await q.answer("ɴᴏᴛ ғᴏʀ ʏᴏᴜ", True)

    await q.answer()

    data = q.data.split("|")[1]

    if data == "close":
        return await q.message.delete()

    if data == "back":

        folders = get_folders()

        buttons = [
            [InlineKeyboardButton(fmt(f), callback_data=f"plug|{f}")]
            for f in folders
        ]

        buttons.append([
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="plug|close")
        ])

        return await q.message.edit(
            "✦ ᴘʟᴜɢɪɴ ᴘᴀɴᴇʟ ✦\n\nsᴇʟᴇᴄᴛ ᴀ ᴄᴀᴛᴇɢᴏʀʏ",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    files = get_files(data)

    if not files:
        return await q.message.edit(
            f"❖ {fmt(data)}\n\nɴᴏ ғɪʟᴇs ғᴏᴜɴᴅ",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="plug|back"),
                    InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="plug|close")
                ]
            ])
        )

    text = f"❖ {fmt(data)}\n\n"

    for f in sorted(files):
        text += f"• {fmt(f)}\n"

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⬅️ ʙᴀᴄᴋ", callback_data="plug|back"),
            InlineKeyboardButton("❌ ᴄʟᴏsᴇ", callback_data="plug|close")
        ]
    ])

    await q.message.edit(
        text + "\n— powered by @theinfinitynetwork",
        reply_markup=kb
    )
