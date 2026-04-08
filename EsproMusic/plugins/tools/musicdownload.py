import asyncio
from pyrogram import Client, filters
from pyrogram.types import Message


@Client.on_message(filters.command(["music"]))
async def send_music(client: Client, message: Message):
    try:
        if len(message.command) < 2:
            return await message.reply_text("❖ Please give a song name")

        song_name = " ".join(message.command[1:])

        msg = await message.reply_text("🔍 Searching...")

        # Inline bot se result
        results = await client.get_inline_bot_results("deezermusicbot", song_name)

        if not results.results:
            return await msg.edit("❌ No results found")

        # Saved messages me bhejna
        saved = await client.send_inline_bot_result(
            chat_id="me",
            query_id=results.query_id,
            result_id=results.results[0].id,
        )

        # Message fetch karna
        saved_msg = await client.get_messages("me", saved.updates[1].message.id)

        # Reply logic (simple)
        reply_to = message.reply_to_message.id if message.reply_to_message else None

        # Audio send
        await client.send_audio(
            chat_id=message.chat.id,
            audio=saved_msg.audio.file_id,
            caption=f"🎵 {song_name}",
            reply_to_message_id=reply_to,
        )

        # Saved message delete
        await client.delete_messages("me", saved_msg.id)

        await msg.delete()

    except Exception as e:
        print(e)
        await message.reply_text("❌ Failed to download song")
