#file written by @itzarjuna01 © some errors spotted were fixed via ai 
#any marks of ai should be considered as ai fixes 
# ================== PLUGIN SHOW SYSTEM ==================

import os
from pyrogram import filters
from pyrogram.types import Message

from EsproMusic import app
from config import OWNER_ID

# ================== GET PLUGINS ==================
def get_plugins():
    plugins = []
    base_path = "EsproMusic/plugins"

    for root, _, files in os.walk(base_path):
        for file in files:
            if file.endswith(".py") and not file.startswith("_"):
                name = file.replace(".py", "")
                plugins.append(name)

    return sorted(plugins)


# ================== FORMAT ==================
def fancy_format(name: str):
    return f"•  **{name.lower()}**"


# ================== COMMAND ==================
@app.on_message(filters.command("showplugins") & filters.group)
async def show_plugins(client, message: Message):

    if message.from_user.id != OWNER_ID:
        return await message.reply_text("ᴏᴡɴᴇʀ ᴏɴʟʏ")

    plugins = get_plugins()

    if not plugins:
        return await message.reply_text("ɴᴏ ᴘʟᴜɢɪɴs ғᴏᴜɴᴅ")

    text = (
        "╭─〔 📦 ᴘʟᴜɢɪɴ ʟɪsᴛ 〕─╮\n"
        "│\n"
    )

    for plugin in plugins:
        text += f"│ {fancy_format(plugin)}\n"

    text += (
        "│\n"
        "╰────────────────╯\n\n"
        "➤ ᴘᴏᴡᴇʀᴇᴅ ʙʏ ᴠᴇᴢ"
    )

    await message.reply_text(text)
