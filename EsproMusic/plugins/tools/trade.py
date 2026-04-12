from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from EsproMusic import Loy
from config import user_collection


pending_trades = {}
pending_gifts = {}


def get_char(user, cid):
    return next((c for c in user.get("characters", []) if c.get("id") == cid), None)


# ================= TRADE =================

@Loy.on_message(filters.command("trade") & filters.group)
async def trade(_, message):

    if not message.reply_to_message:
        return await message.reply("❖ ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ")

    if len(message.command) != 3:
        return await message.reply("❖ /trade your_id other_id")

    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        return await message.reply("❖ ᴄᴀɴᴛ ᴛʀᴀᴅᴇ ʏᴏᴜʀsᴇʟғ")

    s_id, r_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({"id": sender_id})
    receiver = await user_collection.find_one({"id": receiver_id})

    if not sender or not receiver:
        return await message.reply("❖ ᴜsᴇʀ ᴅᴀᴛᴀ ɴᴏᴛ ғᴏᴜɴᴅ")

    sc = get_char(sender, s_id)
    rc = get_char(receiver, r_id)

    if not sc:
        return await message.reply("❖ ʏᴏᴜ ᴅᴏɴᴛ ʜᴀᴠᴇ ᴛʜɪs")

    if not rc:
        return await message.reply("❖ ᴛʜᴇʏ ᴅᴏɴᴛ ʜᴀᴠᴇ ᴛʜɪs")

    pending_trades[(sender_id, receiver_id)] = (s_id, r_id)

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ʏᴇs", callback_data=f"trade_yes|{sender_id}")],
        [InlineKeyboardButton("❌ ɴᴏ", callback_data=f"trade_no|{sender_id}")]
    ])

    await message.reply(
        f"❖ {message.reply_to_message.from_user.mention} ᴀᴄᴄᴇᴘᴛ ᴛʀᴀᴅᴇ?",
        reply_markup=kb
    )


@Loy.on_callback_query(filters.regex("^trade_"))
async def trade_cb(_, q: CallbackQuery):

    data = q.data.split("|")
    action = data[0]
    sender_id = int(data[1])
    receiver_id = q.from_user.id

    key = (sender_id, receiver_id)

    if key not in pending_trades:
        return await q.answer("ɴᴏ ᴛʀᴀᴅᴇ", True)

    if action == "trade_no":
        pending_trades.pop(key, None)
        return await q.message.edit("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ")

    s_id, r_id = pending_trades[key]

    sender = await user_collection.find_one({"id": sender_id})
    receiver = await user_collection.find_one({"id": receiver_id})

    sc = get_char(sender, s_id)
    rc = get_char(receiver, r_id)

    if not sc or not rc:
        return await q.message.edit("❌ ᴇʀʀᴏʀ")

    sender["characters"].remove(sc)
    receiver["characters"].remove(rc)

    sender["characters"].append(rc)
    receiver["characters"].append(sc)

    await user_collection.update_one({"id": sender_id}, {"$set": {"characters": sender["characters"]}})
    await user_collection.update_one({"id": receiver_id}, {"$set": {"characters": receiver["characters"]}})

    pending_trades.pop(key, None)

    await q.message.edit("✅ ᴛʀᴀᴅᴇ sᴜᴄᴄᴇss")


# ================= GIFT =================

@Loy.on_message(filters.command("gift") & filters.group)
async def gift(_, message):

    if not message.reply_to_message:
        return await message.reply("❖ ʀᴇᴘʟʏ ᴛᴏ ᴜsᴇʀ")

    if len(message.command) != 2:
        return await message.reply("❖ /gift char_id")

    sender_id = message.from_user.id
    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        return await message.reply("❖ ɴᴏ sᴇʟғ")

    cid = message.command[1]

    sender = await user_collection.find_one({"id": sender_id})

    if not sender:
        return await message.reply("❖ ɴᴏ ᴅᴀᴛᴀ")

    char = get_char(sender, cid)

    if not char:
        return await message.reply("❖ ɴᴏᴛ ғᴏᴜɴᴅ")

    pending_gifts[(sender_id, receiver_id)] = char

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ʏᴇs", callback_data=f"gift_yes|{receiver_id}")],
        [InlineKeyboardButton("❌ ɴᴏ", callback_data=f"gift_no|{receiver_id}")]
    ])

    await message.reply(
        f"❖ ᴄᴏɴғɪʀᴍ ɢɪғᴛ ᴛᴏ {message.reply_to_message.from_user.mention}?",
        reply_markup=kb
    )


@Loy.on_callback_query(filters.regex("^gift_"))
async def gift_cb(_, q: CallbackQuery):

    data = q.data.split("|")
    action = data[0]
    receiver_id = int(data[1])
    sender_id = q.from_user.id

    key = (sender_id, receiver_id)

    if key not in pending_gifts:
        return await q.answer("ɴᴏ ɢɪғᴛ", True)

    if action == "gift_no":
        pending_gifts.pop(key, None)
        return await q.message.edit("❌ ᴄᴀɴᴄᴇʟʟᴇᴅ")

    char = pending_gifts[key]

    sender = await user_collection.find_one({"id": sender_id})
    receiver = await user_collection.find_one({"id": receiver_id})

    sender["characters"].remove(char)

    await user_collection.update_one({"id": sender_id}, {"$set": {"characters": sender["characters"]}})

    if receiver:
        await user_collection.update_one({"id": receiver_id}, {"$push": {"characters": char}})
    else:
        await user_collection.insert_one({
            "id": receiver_id,
            "characters": [char]
        })

    pending_gifts.pop(key, None)

    await q.message.edit("🎁 ɢɪғᴛ sᴇɴᴛ")
