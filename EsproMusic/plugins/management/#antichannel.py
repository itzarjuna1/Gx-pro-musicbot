from pyrogram import Client, filters
from pyrogram.raw import functions, types
from pyrogram.raw.base import Update
from pyrogram.enums import ChatMemberStatus, ButtonStyle
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

# ================== PATCH (LIKE LOCK FILE) ==================
try:
    ButtonStyle.PRIMARY
except:
    class ButtonStyle:
        PRIMARY = None
        SUCCESS = None

# ================== MONGO ==================
mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
anti_db = db["antichannel"]

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
def is_enabled(chat_id):
    data = anti_db.find_one({"chat_id": chat_id})
    return data.get("enabled", False) if data else False

def toggle(chat_id, state: bool):
    anti_db.update_one(
        {"chat_id": chat_id},
        {"$set": {"enabled": state}},
        upsert=True
    )

# ================== UI ==================
def panel_text(state):
    status = "🟢 ᴇɴᴀʙʟᴇᴅ" if state else "🔴 ᴅɪsᴀʙʟᴇᴅ"
    return (
        "╭─〔 🌸 ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ 🌸 〕─╮\n"
        "│ ᴘʀᴏᴛᴇᴄᴛ ɢʀᴏᴜᴘ ғʀᴏᴍ ᴄʜᴀɴɴᴇʟs\n"
        f"│ sᴛᴀᴛᴜs : {status}\n"
        "╰────────────────────╯"
    )

def panel_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🌷 ᴇɴᴀʙʟᴇ",
                callback_data="anti_on",
                style=ButtonStyle.SUCCESS
            ),
            InlineKeyboardButton(
                "🥀 ᴅɪsᴀʙʟᴇ",
                callback_data="anti_off",
                style=ButtonStyle.PRIMARY
            )
        ]
    ])

# ================== COMMAND ==================
@app.on_message(filters.command("antichannel") & filters.group)
async def antichannel_cmd(client, message):
    if not await is_admin(client, message.chat.id, message.from_user.id):
        return await message.reply("🌸 ᴀᴅᴍɪɴs ᴏɴʟʏ")

    state = is_enabled(message.chat.id)

    await message.reply(
        panel_text(state),
        reply_markup=panel_buttons()
    )

# ================== CALLBACK ==================
@app.on_callback_query()
async def anti_callback(client, query):
    chat_id = query.message.chat.id
    user_id = query.from_user.id

    if not await is_admin(client, chat_id, user_id):
        return await query.answer("admins only", show_alert=True)

    if query.data == "anti_on":
        toggle(chat_id, True)

    elif query.data == "anti_off":
        toggle(chat_id, False)

    state = is_enabled(chat_id)

    await query.message.edit_text(
        panel_text(state),
        reply_markup=panel_buttons()
    )

    await query.answer("🌷 ᴜᴘᴅᴀᴛᴇᴅ")

# ================== RAW HANDLER ==================
@Client.on_raw_update()
async def channel_handler(client: Client, update: Update, _, chats: dict):
    try:
        if not isinstance(update, types.UpdateNewChannelMessage):
            return

        if not isinstance(update.message.from_id, types.PeerChannel):
            return

        message = update.message
        chat_id = int(f"-100{message.peer_id.channel_id}")
        channel_id = int(f"-100{message.from_id.channel_id}")

        if not is_enabled(chat_id):
            return

        # ignore linked channel
        if (
            message.fwd_from
            and message.fwd_from.saved_from_peer
            == message.fwd_from.from_id
            == message.from_id
        ) or channel_id == chat_id:
            return

        # ban
        await client.send(
            functions.channels.EditBanned(
                channel=await client.resolve_peer(chat_id),
                participant=await client.resolve_peer(channel_id),
                banned_rights=types.ChatBannedRights(
                    until_date=0,
                    view_messages=True,
                    send_messages=True,
                    send_media=True,
                    send_stickers=True,
                    send_gifs=True,
                    send_games=True,
                    send_polls=True,
                ),
            )
        )

        # delete
        await client.delete_messages(chat_id, message.id)

        # aesthetic log 🌸
        await client.send_message(
            chat_id,
            "╭─〔 🌸 ᴀɴᴛɪ ᴄʜᴀɴɴᴇʟ 🌸 〕─╮\n"
            f"│ ᴄʜᴀɴɴᴇʟ : `{channel_id}`\n"
            "│ ᴀᴄᴛɪᴏɴ : ʙᴀɴ + ᴅᴇʟᴇᴛᴇ\n"
            "╰────────────────────╯",
            disable_web_page_preview=True,
        )

    except Exception as e:
        print(e)
