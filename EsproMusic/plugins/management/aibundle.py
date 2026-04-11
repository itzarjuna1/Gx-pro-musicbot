import requests
import random
import asyncio

from pyrogram import filters
from pyrogram.types import Message
from pymongo import MongoClient

from EsproMusic import app
from config import MONGO_DB_URI

mongo = MongoClient(MONGO_DB_URI)
db = mongo["musicbot"]
ai_db = db["ai_persona"]

DEFAULT_PERSONA = "gpt"


def set_persona(user_id, persona):
    ai_db.update_one(
        {"user_id": user_id},
        {"$set": {"persona": persona}},
        upsert=True
    )

def get_persona(user_id):
    data = ai_db.find_one({"user_id": user_id})
    return data["persona"] if data else DEFAULT_PERSONA

PERSONAS = ["gpt", "claude", "grok", "deepseek"]

@app.on_message(filters.command("setpersona"))
async def setpersona(client, message: Message):

    if len(message.command) < 2:
        return await message.reply(
            "⚙️ **Available Personas:**\n\n"
            "• gpt\n• claude\n• grok\n• deepseek\n\n"
            "Use ➜ /setpersona gpt"
        )

    persona = message.command[1].lower()

    if persona not in PERSONAS:
        return await message.reply("❌ Invalid persona")

    set_persona(message.from_user.id, persona)

    await message.reply(f"✅ Persona set to **{persona.upper()}**")

@app.on_message(filters.command("ai"))
async def ai_chat(client, message: Message):

    if len(message.command) < 2:
        return await message.reply("❌ Use ➜ /ai <question>")

    query = message.text.split(None, 1)[1]
    persona = get_persona(message.from_user.id)

    msg = await message.reply("🤖 Thinking...")

    try:
        url = f"https://text.pollinations.ai/{query}"

        res = requests.get(url, timeout=10)
        reply = res.text[:4000]

        await msg.edit(
            f"🤖 **{persona.upper()} AI**\n\n{reply}"
        )

    except:
        await msg.edit("❌ AI failed to respond")

@app.on_message(filters.command("draw"))
async def draw(client, message: Message):

    if len(message.command) < 2:
        return await message.reply("❌ Use ➜ /draw <prompt>")

    prompt = message.text.split(None, 1)[1]

    img_url = f"https://image.pollinations.ai/prompt/{prompt}"

    await message.reply_photo(
        img_url,
        caption=f"🎨 **Generated Image**\n\nPrompt: `{prompt}`"
    )


games = {}

@app.on_message(filters.command("guess"))
async def guess_start(client, message: Message):

    num = random.randint(1, 10)
    games[message.from_user.id] = num

    await message.reply("🎮 Guess number (1-10)\nSend number now!")

@app.on_message(filters.text & filters.private)
async def guess_play(client, message: Message):

    if message.from_user.id not in games:
        return

    try:
        user_guess = int(message.text)
    except:
        return

    real = games[message.from_user.id]

    if user_guess == real:
        del games[message.from_user.id]
        await message.reply("🎉 Correct!")
    else:
        await message.reply("❌ Wrong, try again")

@app.on_message(filters.voice)
async def voice_ai(client, message: Message):

    msg = await message.reply("🎤 Processing voice...")

    try:
        file = await message.download()


        await asyncio.sleep(2)

        await msg.edit(
            "🧠 Voice received!\n\n(Real speech recognition can be added with Whisper API)"
        )

    except:
        await msg.edit("❌ Failed to process voice")

@app.on_message(filters.command("aihelp"))
async def aihelp(client, message: Message):

    await message.reply(
        "🤖 **AI SYSTEM COMMANDS**\n\n"
        "/setpersona gpt/claude/grok/deepseek\n"
        "/ai <question>\n"
        "/draw <prompt>\n"
        "/guess (game)\n"
        "/aihelp\n"
      )
