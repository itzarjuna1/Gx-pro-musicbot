# EsproMusic/plugins/tools/assistantlogger.py
import asyncio
from pyrogram import filters
from pyrogram.types import Message
from pyrogram.raw import functions
from pyrogram.raw.functions.phone import GetGroupCall
from pyrogram.raw.types import InputGroupCall
from pytgcalls import PyTgCalls
from pytgcalls.types import Update
from EsproMusic.core.userbot import Userbot, assistants

# Initialize PyTgCalls for each assistant
calls = []

for idx, client_num in enumerate(assistants):
    # get actual Client instance from Userbot
    client_instance = getattr(Userbot(), f"{['one','two','three','four','five'][client_num-1]}")
    calls.append(PyTgCalls(client_instance))

async def tts_vc_logger(client: Userbot, call: PyTgCalls):
    @client.one.on_raw_update()
    async def handler(update, users):
        # Only listen for voice chat join updates
        if hasattr(update, "participants") and update.participants:
            for p in update.participants:
                user_id = p.user_id
                username = users.get(user_id).first_name if users.get(user_id) else str(user_id)
                # send TTS message
                msg = await client.one.send_message(
                    chat_id=call.chat_id,
                    text=f"/tts {username} has joined vc"
                )
                # automatically playforce TTS reply
                await asyncio.sleep(1)
                tts_reply = (await client.one.get_chat_history(call.chat_id, limit=1))[0]
                await client.one.send_message(
                    chat_id=call.chat_id,
                    text=f"/playforce {tts_reply.message_id}"
                )
                # delete command msg after sending
                await msg.delete()

async def main():
    userbot = Userbot()
    await userbot.start()
    for call in calls:
        await tts_vc_logger(userbot, call)

if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())
