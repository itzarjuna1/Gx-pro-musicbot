# ================== RULES SYSTEM ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== DB ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
rules_db = db["rules"]

# ================== ADMIN ==================
async def is_admin(client, chat_id, user_id):
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (
            ChatMemberStatus.ADMINISTRATOR,
            ChatMemberStatus.OWNER
        )
    except:
        return False

# ================== DB ==================
def get_rules(chat_id):
    return rules_db.find_one({"chat_id": chat_id}) or {}

def set_rules(chat_id, text):
    rules_db.update_one({"chat_id": chat_id}, {"$set": {"rules": text}}, upsert=True)

def reset_rules(chat_id):
    rules_db.delete_one({"chat_id": chat_id})

def set_private(chat_id, value):
    rules_db.update_one({"chat_id": chat_id}, {"$set": {"private": value}}, upsert=True)

def set_button(chat_id, name):
    rules_db.update_one({"chat_id": chat_id}, {"$set": {"button": name}}, upsert=True)

# ================== /rules ==================
@app.on_message(filters.command("rules") & filters.group)
async def rules(client, message: Message):
    data = get_rules(message.chat.id)

    text = data.get("rules", "ɴᴏ ʀᴜʟᴇs sᴇᴛ.")
    private = data.get("private", False)
    button_name = data.get("button", "📜 ʀᴜʟᴇs")

    # noformat
    if len(message.command) > 1 and message.command[1].lower() == "noformat":
        return await message.reply_text(text)

    if private:
        btn = InlineKeyboardMarkup(
            [[
                InlineKeyboardButton(
                    button_name,
                    url=f"https://t.me/{(await client.get_me()).username}?start=rules_{message.chat.id}",
                    style=ButtonStyle.PREMIUM
                )
            ]]
        )
        return await message.reply_text(
            "📜 ᴄʟɪᴄᴋ ʙᴇʟᴏᴡ ᴛᴏ ᴠɪᴇᴡ ʀᴜʟᴇs.",
            reply_markup=btn
        )

    await message.reply_text(text)

# ================== PRIVATE RULES ==================
@app.on_message(filters.private & filters.regex(r"^/start rules_(\d+)"))
async def private_rules(client, message: Message):
    chat_id = int(message.matches[0].group(1))
    data = get_rules(chat_id)

    text = data.get("rules", "ɴᴏ ʀᴜʟᴇs sᴇᴛ.")

    await message.reply_text(text)

# ================== SET RULES ==================
@app.on_message(filters.command("setrules") & filters.group)
async def setrules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ: /setrules <ᴛᴇxᴛ>")

    text = message.text.split(None, 1)[1]
    set_rules(message.chat.id, text)

    await message.reply("✅ ʀᴜʟᴇs sᴇᴛ")

# ================== RESET RULES ==================
@app.on_message(filters.command("resetrules") & filters.group)
async def resetrules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    reset_rules(message.chat.id)
    await message.reply("♻️ ʀᴜʟᴇs ʀᴇsᴇᴛ")

# ================== PRIVATE TOGGLE ==================
@app.on_message(filters.command("privaterules") & filters.group)
async def privaterules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ: /privaterules yes/no")

    val = message.command[1].lower()
    state = val in ["yes", "on", "true"]

    set_private(message.chat.id, state)

    await message.reply(
        f"🔐 ᴘʀɪᴠᴀᴛᴇ ʀᴜʟᴇs: {'ᴇɴᴀʙʟᴇᴅ' if state else 'ᴅɪsᴀʙʟᴇᴅ'}"
    )

# ================== SET BUTTON ==================
@app.on_message(filters.command("setrulesbutton") & filters.group)
async def setrulesbutton(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ: /setrulesbutton <ɴᴀᴍᴇ>")

    name = message.text.split(None, 1)[1]
    set_button(message.chat.id, name)

    await message.reply("🔘 ʙᴜᴛᴛᴏɴ ᴜᴘᴅᴀᴛᴇᴅ")

# ================== RESET BUTTON ==================
@app.on_message(filters.command("resetrulesbutton") & filters.group)
async def resetrulesbutton(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("ᴀᴅᴍɪɴs ᴏɴʟʏ")

    set_button(message.chat.id, "📜 ʀᴜʟᴇs")

    await message.reply("♻️ ʙᴜᴛᴛᴏɴ ʀᴇsᴇᴛ")
