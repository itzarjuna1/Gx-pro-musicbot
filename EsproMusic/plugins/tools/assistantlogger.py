
from pyrogram import Client, filters
from pyrogram.types import Message
from EsproMusic.core.userbot import Userbot, assistants
from gtts import gTTS
import asyncio
import os

userbot = Userbot()

async def tts_and_play(client: Client, chat_id: int, username: str):
    """Generate TTS and play in VC with fallback"""
    text = f"{username} has joined VC"
    tts_file = f"tts_{chat_id}.mp3"
    
    # generate TTS
    tts = gTTS(text=text, lang="en")
    tts.save(tts_file)

    # send TTS message
    msg = await client.send_message(chat_id, f"/tts {text}")
    
    # determine which play command to use
    try:
        # If a song is already playing, use /playforce
        if client.is_connected:  # check if bot is connected to VC
            await client.send_message(chat_id, f"/playforce {msg.message_id}")
        else:
            # fallback to normal play
            await client.send_message(chat_id, f"/play {tts_file}")
    except Exception:
        # fallback if any error occurs
        await client.send_message(chat_id, f"/play {tts_file}")

    # delete the command message
    try:
        await msg.delete()
    except:
        pass

    # remove local file
    if os.path.exists(tts_file):
        os.remove(tts_file)


# Pyrogram handler for when someone joins VC
@userbot.one.on_raw_update()
async def vc_logger_handler(_, update, users, chats):
    """Detect VC joins and trigger TTS"""
    try:
        from pytgcalls.types import Update
        from pytgcalls.types.chats import GroupCallParticipant

        if isinstance(update, GroupCallParticipant) and update.joined:
            user_id = update.user_id
            # fetch username or fallback to user_id
            user = await userbot.one.get_users(user_id)
            username = user.first_name if user.first_name else str(user_id)
            await tts_and_play(userbot.one, update.chat_id, username)
    except Exception as e:
        print(f"VC Logger Error: {e}")


# repeat handler registration for other assistants
for idx, client in enumerate([userbot.two, userbot.three, userbot.four, userbot.five], start=2):
    if client:
        @client.on_raw_update()
        async def vc_logger_handler_multi(_, update, users, chats, client=client):
            try:
                from pytgcalls.types import Update
                from pytgcalls.types.chats import GroupCallParticipant

                if isinstance(update, GroupCallParticipant) and update.joined:
                    user_id = update.user_id
                    user = await client.get_users(user_id)
                    username = user.first_name if user.first_name else str(user_id)
                    await tts_and_play(client, update.chat_id, username)
            except Exception as e:
                print(f"VC Logger Error (Assistant {idx}): {e}")
