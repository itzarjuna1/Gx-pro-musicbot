import asyncio
import os

from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app
from EsproMusic import userbot as us
from EsproMusic.core.userbot import assistants


@app.on_message(filters.command("music"))
async def music_handler(client: Client, message: Message):
    msg = await message.reply("<code>🔍 Searching...</code>")

    # Query check
    if len(message.command) < 2:
        return await msg.edit("<code>Usage: /music song name</code>")

    query = " ".join(message.command[1:])

    # Assistant check
    if 1 in assistants:
        ubot = us.one
    else:
        return await msg.edit("<code>Userbot assistant not found.</code>")

    try:
        # 🔥 Step 1: Assistant se inline search
        results = await ubot.get_inline_bot_results("deezermusicbot", query)

        if not results.results:
            return await msg.edit("<code>❌ No results found</code>")

        # 🔥 Step 2: Sirf audio result pick karo
        audio_result = None
        for res in results.results:
            if res.type == "audio":
                audio_result = res
                break

        if not audio_result:
            return await msg.edit("<code>❌ No downloadable audio found</code>")

        # 🔥 Step 3: Assistant se Saved Messages me send
        sent = await ubot.send_inline_bot_result(
            chat_id="me",
            query_id=results.query_id,
            result_id=audio_result.id,
        )

        await asyncio.sleep(2)

        saved_msg = None

        # ✅ CASE 1: direct Message
        if isinstance(sent, Message):
            saved_msg = sent

        # ✅ CASE 2: updates wala
        elif hasattr(sent, "updates"):
            for upd in sent.updates:
                if hasattr(upd, "message") and upd.message:
                    saved_msg = upd.message
                    break

        if not saved_msg:
            return await msg.edit("<code>❌ Failed to fetch song</code>")

        # Proper fetch
        saved_msg = await ubot.get_messages("me", saved_msg.id)

        # ❌ Safety check
        if not saved_msg.audio:
            return await msg.edit("<code>❌ No audio found</code>")

        # 🔥 Step 4: Download via assistant
        file_path = await ubot.download_media(saved_msg.audio.file_id)

        # Reply logic
        reply_to = message.reply_to_message.id if message.reply_to_message else None

        # 🔥 Step 5: Send via BOT (reupload)
        await client.send_audio(
            chat_id=message.chat.id,
            audio=file_path,
            caption=f"🎵 **{query}**",
            reply_to_message_id=reply_to,
        )

        # 🧹 Cleanup
        await ubot.delete_messages("me", saved_msg.id)

        if os.path.exists(file_path):
            os.remove(file_path)

        await msg.delete()

    except Exception as e:
        print("ERROR:", e)
        await msg.edit("<code>❌ Failed to fetch song</code>")
