# ================== ROSE STYLE RULES SYSTEM (FINAL) ==================

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, Message
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== DB ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
rules_db = db["rules"]

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

# ================== DB FUNCTIONS ==================
def get_data(chat_id):
    data = rules_db.find_one({"chat_id": chat_id})
    return data if data else {}

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

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    name,
                    callback_data="show_rules",
                    style=ButtonStyle.PRIMARY
                )
            ]
        ]
    )

# ================== SET RULES ==================
@app.on_message(filters.command("setrules") & filters.group)
async def setrules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /setrules <ᴛᴇxᴛ>")

    text = message.text.split(None, 1)[1]
    set_rules(message.chat.id, text)

    await message.reply("✅ ʀᴜʟᴇs sᴇᴛ sᴜᴄᴄᴇssғᴜʟʟʏ")

# ================== GET RULES ==================
@app.on_message(filters.command("rules") & filters.group)
async def rules(client, message: Message):
    data = get_data(message.chat.id)

    if "rules" not in data:
        return await message.reply("❌ ɴᴏ ʀᴜʟᴇs sᴇᴛ")

    text = data["rules"]

    # ROSE STYLE FLOW
    if "{rules}" in text:
        msg = text.replace("{rules}", "").strip()

        await message.reply(
            msg,
            reply_markup=build_button(message.chat.id)
        )
    else:
        await message.reply(text)

# ================== CALLBACK ==================
@app.on_callback_query(filters.regex("^show_rules$"))
async def show_rules(client, query):
    data = get_data(query.message.chat.id)

    if "rules" not in data:
        return await query.answer("ɴᴏ ʀᴜʟᴇs", show_alert=True)

    text = data["rules"].replace("{rules}", "").strip()
    private = data.get("private", False)

    bot_username = (await client.get_me()).username

    # PRIVATE RULES MODE
    if private:
        try:
            await client.send_message(
                query.from_user.id,
                f"📜 **ʀᴜʟᴇs**\n\n{text}"
            )
            return await query.answer("📩 ᴄʜᴇᴄᴋ ᴘᴍ", show_alert=True)

        except:
            return await query.message.reply(
                "⚠️ ᴘʟᴇᴀsᴇ sᴛᴀʀᴛ ᴍᴇ ғɪʀsᴛ",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🚀 sᴛᴀʀᴛ ʙᴏᴛ",
                                url=f"https://t.me/waifuxmusicbot?start=rules"
                            )
                        ]
                    ]
                )
            )

    else:
        await query.answer()
        await query.message.reply(f"📜 **ʀᴜʟᴇs**\n\n{text}")

# ================== PRIVATE TOGGLE ==================
@app.on_message(filters.command("privaterules") & filters.group)
async def privaterules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /privaterules on/off")

    arg = message.command[1].lower()

    if arg in ["on", "yes", "true"]:
        set_private(message.chat.id, True)
        await message.reply("✅ ᴘʀɪᴠᴀᴛᴇ ʀᴜʟᴇs ᴇɴᴀʙʟᴇᴅ")

    elif arg in ["off", "no", "false"]:
        set_private(message.chat.id, False)
        await message.reply("❌ ᴘʀɪᴠᴀᴛᴇ ʀᴜʟᴇs ᴅɪsᴀʙʟᴇᴅ")

# ================== SET BUTTON NAME ==================
@app.on_message(filters.command("setrulesbutton") & filters.group)
async def setrulesbutton(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    if len(message.command) < 2:
        return await message.reply("ᴜsᴇ ➠ /setrulesbutton <ɴᴀᴍᴇ>")

    name = message.text.split(None, 1)[1]
    set_button(message.chat.id, name)

    await message.reply("✅ ʙᴜᴛᴛᴏɴ ᴜᴘᴅᴀᴛᴇᴅ")

# ================== RESET BUTTON ==================
@app.on_message(filters.command("resetrulesbutton") & filters.group)
async def resetrulesbutton(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    set_button(message.chat.id, "📜 ʀᴜʟᴇs")
    await message.reply("♻️ ʙᴜᴛᴛᴏɴ ʀᴇsᴇᴛ")

# ================== RESET RULES ==================
@app.on_message(filters.command("resetrules") & filters.group)
async def resetrules(client, message: Message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("❌ ᴀᴅᴍɪɴs ᴏɴʟʏ")

    reset_all(message.chat.id)
    await message.reply("♻️ ʀᴜʟᴇs ʀᴇsᴇᴛ")
