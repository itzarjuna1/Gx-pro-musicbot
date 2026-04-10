from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message
)
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== PATCH ==================
try:
    ButtonStyle.PRIMARY
except:
    class ButtonStyle:
        PRIMARY = None
        SUCCESS = None

# ================== MONGO ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
approve_db = db["approve"]

# ================== ADMIN ==================
async def is_admin(client, message: Message):
    try:
        member = await client.get_chat_member(
            message.chat.id,
            message.from_user.id
        )
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

# ================== DB ==================
def get_approved(chat_id):
    data = approve_db.find_one({"chat_id": chat_id})
    return data.get("users", []) if data else []

def approve_user(chat_id, user_id):
    approve_db.update_one(
        {"chat_id": chat_id},
        {"$addToSet": {"users": user_id}},
        upsert=True
    )

def disapprove_user(chat_id, user_id):
    approve_db.update_one(
        {"chat_id": chat_id},
        {"$pull": {"users": user_id}}
    )

def unapprove_all(chat_id):
    approve_db.delete_one({"chat_id": chat_id})

# ================== TEXT ==================
def main_text():
    return (
        "╭─〔 🌸 ᴀᴘᴘʀᴏᴠᴇ sʏsᴛᴇᴍ 🌸 〕─╮\n"
        "│ ᴍᴀɴᴀɢᴇ ᴛʀᴜsᴛᴇᴅ ᴜsᴇʀs\n"
        "╰────────────────────╯"
    )

def confirm_text():
    return (
        "╭─〔 ⚠️ ᴄᴏɴғɪʀᴍ ⚠️ 〕─╮\n"
        "│ ᴜɴᴀᴘᴘʀᴏᴠᴇ ᴀʟʟ ᴜsᴇʀs?\n"
        "╰────────────────────╯"
    )

# ================== APPROVE ==================
@app.on_message(filters.command("approve") & filters.group)
async def approve(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("🌸 ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if not message.reply_to_message:
        return await message.reply("ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ")

    user = message.reply_to_message.from_user
    approve_user(message.chat.id, user.id)

    await message.reply(
        f"🌷 {user.first_name} ɪs ɴᴏᴡ ᴀᴘᴘʀᴏᴠᴇᴅ"
    )

# ================== DISAPPROVE ==================
@app.on_message(filters.command("unapprove") & filters.group)
async def disapprove(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("admins only")

    if not message.reply_to_message:
        return await message.reply("reply to user")

    user = message.reply_to_message.from_user
    disapprove_user(message.chat.id, user.id)

    await message.reply(
        f"🥀 {user.first_name} ʀᴇᴍᴏᴠᴇᴅ ғʀᴏᴍ ᴀᴘᴘʀᴏᴠᴇᴅ"
    )

# ================== LIST ==================
@app.on_message(filters.command("approved") & filters.group)
async def approved_list(client, message: Message):
    users = get_approved(message.chat.id)

    if not users:
        return await message.reply("ɴᴏ ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs")

    text = "╭─〔 🌸 ᴀᴘᴘʀᴏᴠᴇᴅ ᴜsᴇʀs 🌸 〕─╮\n"

    for uid in users:
        try:
            user = await client.get_users(uid)
            text += f"│ {user.first_name}\n"
        except:
            text += f"│ {uid}\n"

    text += "╰────────────────────╯"

    await message.reply(text)

# ================== CHECK ==================
@app.on_message(filters.command("approval") & filters.group)
async def approval(client, message: Message):
    if not message.reply_to_message:
        return await message.reply("reply to user")

    user = message.reply_to_message.from_user
    users = get_approved(message.chat.id)

    if user.id in users:
        await message.reply(
            f"🟢 {user.first_name} ɪs ᴀᴘᴘʀᴏᴠᴇᴅ"
        )
    else:
        await message.reply(
            f"🔴 {user.first_name} ɪs ɴᴏᴛ ᴀᴘᴘʀᴏᴠᴇᴅ"
        )

# ================== UNAPPROVE ALL ==================
@app.on_message(filters.command("unapproveall") & filters.group)
async def unapprove_all_cmd(client, message: Message):
    if not await is_admin(client, message):
        return await message.reply("admins only")

    await message.reply(
        confirm_text(),
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🌷 ʏᴇs",
                    callback_data="unapprove_yes",
                    style=ButtonStyle.SUCCESS
                ),
                InlineKeyboardButton(
                    "🥀 ɴᴏ",
                    callback_data="unapprove_no",
                    style=ButtonStyle.PRIMARY
                )
            ]
        ])
    )

# ================== CALLBACK ==================
@app.on_callback_query()
async def approve_callbacks(client, query):
    chat_id = query.message.chat.id

    if query.data == "unapprove_yes":
        unapprove_all(chat_id)

        await query.message.edit_text(
            "🌸 ᴀʟʟ ᴜsᴇʀs ᴜɴᴀᴘᴘʀᴏᴠᴇᴅ"
        )

    elif query.data == "unapprove_no":
        await query.message.edit_text(
            "🥀 ᴄᴀɴᴄᴇʟʟᴇᴅ"
        )

    await query.answer()
