import asyncio

from pyrogram import Client, filters
from pyrogram.types import Message

from EsproMusic import app
from EsproMusic import userbot as us
from EsproMusic.core.userbot import assistants


@app.on_message(filters.command("music"))
async def music_handler(client: Client, message: Message):
    msg = await message.reply("<code>🔍 Searching...</code>")

    # Song name lena
    if len(message.command) < 2:
        return await msg.edit("<code>Usage: /music song name</code>")

    query = " ".join(message.command[1:])

    # Assistant check
    if 1 in assistants:
        ubot = us.one
    else:
        return await msg.edit("<code>Userbot assistant not found.</code>")

    try:
        # Inline bot results fetch karega userbot
        results = await ubot.get_inline_bot_results("deezermusicbot", query)

        if not results.results:
            return await msg.edit("<code>No results found.</code>")

        # Saved messages me bhejega (userbot side)
        saved = await ubot.send_inline_bot_result(
            chat_id="me",
            query_id=results.query_id,
            result_id=results.results[0].id,
        )

        await asyncio.sleep(1)

        # Message fetch karega
        saved_msg = await ubot.get_messages("me", saved.updates[1].message.id)

        # Main bot se send karega group me
        reply_to = message.reply_to_message.id if message.reply_to_message else None

        await client.send_audio(
            chat_id=message.chat.id,
            audio=saved_msg.audio.file_id,
            caption=f"🎵 **{query}**",
            reply_to_message_id=reply_to,
        )

        # Cleanup (userbot side)
        await ubot.delete_messages("me", saved_msg.id)

        await msg.delete()

    except Exception as e:
        print(e)
        await msg.edit("<code>❌ Failed to fetch song</code>")
