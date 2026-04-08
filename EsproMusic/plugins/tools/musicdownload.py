import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app
from EsproMusic import userbot as us
from EsproMusic.core.userbot import assistants


@app.on_message(filters.command("music"))
async def music_handler(client: Client, message: Message):
    msg = await message.reply("<code>🔍 Searching...</code>")

    if len(message.command) < 2:
        return await msg.edit("<code>Usage: /music song name</code>")

    query = " ".join(message.command[1:])

    # Assistant check
    if 1 in assistants:
        ubot = us.one
    else:
        return await msg.edit("<code>Userbot assistant not found.</code>")

    try:
        # 🔥 Inline search via assistant
        results = await ubot.get_inline_bot_results("deezermusicbot", query)

        if not results.results:
            return await msg.edit("<code>❌ No results found</code>")

        # 🔥 Send via assistant
        sent = await ubot.send_inline_bot_result(
            chat_id="me",
            query_id=results.query_id,
            result_id=results.results[0].id,
        )

        await asyncio.sleep(2)

        saved_msg = None

        # ✅ CASE 1: Direct Message
        if isinstance(sent, Message):
            saved_msg = sent

        # ✅ CASE 2: updates wala case
        elif hasattr(sent, "updates"):
            for upd in sent.updates:
                if hasattr(upd, "message") and upd.message:
                    saved_msg = upd.message
                    break

        if not saved_msg:
            return await msg.edit("<code>❌ Failed to fetch song from assistant</code>")

        # Ensure proper fetch
        saved_msg = await ubot.get_messages("me", saved_msg.id)

        # Reply logic
        reply_to = message.reply_to_message.id if message.reply_to_message else None

        # 🎵 Send audio via main bot
        await client.send_audio(
            chat_id=message.chat.id,
            audio=saved_msg.audio.file_id,
            caption=f"🎵 **{query}**",
            reply_to_message_id=reply_to,
        )

        # 🧹 Cleanup assistant side
        await ubot.delete_messages("me", saved_msg.id)

        await msg.delete()

    except Exception as e:
        print("ERROR:", e)
        await msg.edit("<code>❌ Failed to fetch song</code>")
