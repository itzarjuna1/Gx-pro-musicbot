import asyncio
import time

from pyrogram import Client, filters
from pyrogram.types import Message
from pytgcalls.types import Update
from pytgcalls.types.chats import GroupCallParticipant

# IMPORT YOUR ASSISTANT (USERBOT)
from EsproMusic.core.userbot import userbot as assistant

# ================= CONFIG ================= #

USER_COOLDOWN = 30  # seconds
VC_LOGGER = {}
JOIN_COOLDOWN = {}

# ========================================== #


def can_announce(user_id: int) -> bool:
    now = time.time()
    if user_id in JOIN_COOLDOWN:
        if now - JOIN_COOLDOWN[user_id] < USER_COOLDOWN:
            return False
    JOIN_COOLDOWN[user_id] = now
    return True


async def wait_for_tts_reply(chat_id: int, reply_to_id: int, timeout: int = 20):
    """Wait for TTS reply (audio/voice)"""
    for _ in range(timeout):
        async for msg in assistant.get_chat_history(chat_id, limit=10):
            if msg.reply_to_message_id == reply_to_id and (msg.audio or msg.voice):
                return msg
        await asyncio.sleep(1)
    return None


async def handle_join(chat_id: int, user_id: int):
    try:
        if not VC_LOGGER.get(chat_id, False):
            return

        if not can_announce(user_id):
            return

        user = await assistant.get_users(user_id)
        name = user.first_name or "User"

        text = f"{name} has joined the voice chat"

        # send TTS command
        tts_msg = await assistant.send_message(chat_id, f"/tts {text}")

        # wait for TTS reply
        tts_reply = await wait_for_tts_reply(chat_id, tts_msg.id)

        if not tts_reply:
            return

        # force play that audio
        await assistant.send_message(
            chat_id,
            "/playforce",
            reply_to_message_id=tts_reply.id
        )

    except Exception as e:
        print(f"[VC LOGGER ERROR]: {e}")


# ================= RAW VC LISTENER ================= #

@assistant.on_raw_update()
async def vc_logger_handler(_, update: Update, users, chats):
    try:
        if not hasattr(update, "participants"):
            return

        chat_id = getattr(update, "chat_id", None)
        if not chat_id:
            return

        for participant in update.participants:
            if isinstance(participant, GroupCallParticipant):
                if getattr(participant, "just_joined", False):
                    user_id = participant.user_id
                    await handle_join(chat_id, user_id)

    except Exception as e:
        print(f"[VC RAW ERROR]: {e}")


# ================= TOGGLE COMMAND ================= #

@Client.on_message(filters.command("vclogger"))
async def toggle_vc_logger(client: Client, message: Message):
    chat_id = message.chat.id

    current = VC_LOGGER.get(chat_id, False)
    VC_LOGGER[chat_id] = not current

    status = "Enabled" if VC_LOGGER[chat_id] else "Disabled"
    await message.reply_text(f"VC Logger: {status}")
