#file errors fixed via costum ai
# ================== ROSE STYLE RULES SYSTEM (FINAL FIXED) ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMemberStatus
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== DB ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
rules_db = db["rules"]

BOT_USERNAME = "waifuxmusicbot"

# ================== ADMIN CHECK ==================
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
def get_data(chat_id):
    return rules_db.find_one({"chat_id": chat_id}) or {}

def set_rules(chat_id, text):
    rules_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"rules": text}},
        upsert=True
    )

def set_private(chat_id, value):
    rules_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"private": value}},
        upsert=True
    )

def set_button(chat_id, name):
    rules_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"button": name}},
        upsert=True
    )

def reset_all(chat_id):
    rules_db.delete_one({"chat_id": chat_id})

# ================== BUTTON ==================
def build_button(chat_id):
    data = get_data(chat_id)
    name = data.get("button", "📜 ʀᴜʟᴇs")

    deep_link = f"https://t.me/{BOT_USERNAME}?start=rules_{chat_id}"

    return InlineKeyboardMarkup(
        [[InlineKeyboardButton(name, url=deep_link)]]
    )

# ================== SET RULES ==================
@app.on_message(filters.command("setrules") & filters.group)
async def setrules_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /setrules <ᴛᴇxᴛ>")

    text = message.text.split(None, 1)[1]
    set_rules(message.chat.id, text)

    await message.reply("✅ ʀᴜʟᴇs sᴇᴛ")

# ================== GET RULES ==================
@app.on_message(filters.command("rules") & filters.group)
async def rules_cmd(client, message: Message):
    data = get_data(message.chat.id)

    if "rules" not in data:
        return await message.reply("❌ ɴᴏ ʀᴜʟᴇs sᴇᴛ")

    text = data["rules"]

    if "{rules}" in text:
        msg = text.replace("{rules}", "").strip()

        await message.reply(
            msg,
            reply_markup=build_button(message.chat.id)
        )
    else:
        await message.reply(text)

# ================== START HANDLER (DM RULES) ==================
@app.on_message(filters.command("start") & filters.private)
async def start_handler(client, message: Message):

    if len(message.command) > 1:
        data = message.command[1]

        if data.startswith("rules_"):
            chat_id = int(data.split("_")[1])
            data_db = get_data(chat_id)

            if "rules" not in data_db:
                return await message.reply("❌ ɴᴏ ʀᴜʟᴇs sᴇᴛ")

            text = data_db["rules"].replace("{rules}", "").strip()

            return await message.reply(
                f"📜 **ʀᴜʟᴇs ғᴏʀ ᴄʜᴀᴛ {chat_id}**\n\n{text}"
            )

    await message.reply("✨ ʙᴏᴛ ɪs ᴀʟɪᴠᴇ!")

# ================== PRIVATE TOGGLE ==================
@app.on_message(filters.command("privaterules") & filters.group)
async def privaterules_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /privaterules on/off")

    arg = message.command[1].lower()

    if arg in ["on", "yes"]:
        set_private(message.chat.id, True)
        await message.reply("✅ ᴘʀɪᴠᴀᴛᴇ ᴍᴏᴅᴇ ᴏɴ")

    elif arg in ["off", "no"]:
        set_private(message.chat.id, False)
        await message.reply("❌ ᴘʀɪᴠᴀᴛᴇ ᴍᴏᴅᴇ ᴏғғ")

# ================== SET BUTTON ==================
@app.on_message(filters.command("setrulesbutton") & filters.group)
async def setrulesbutton_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /setrulesbutton <ɴᴀᴍᴇ>")

    name = message.text.split(None, 1)[1]
    set_button(message.chat.id, name)

    await message.reply("✅ ʙᴜᴛᴛᴏɴ ᴜᴘᴅᴀᴛᴇᴅ")

# ================== RESET BUTTON ==================
@app.on_message(filters.command("resetrulesbutton") & filters.group)
async def resetbtn_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    set_button(message.chat.id, "📜 ʀᴜʟᴇs")
    await message.reply("♻️ ʙᴜᴛᴛᴏɴ ʀᴇsᴇᴛ")

# ================== RESET RULES ==================
@app.on_message(filters.command("resetrules") & filters.group)
async def resetrules_cmd(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    reset_all(message.chat.id)
    await message.reply("♻️ ʀᴜʟᴇs ʀᴇsᴇᴛ")
