from pyrogram.types import InlineKeyboardButton

import config
from EsproMusic import app


def start_panel(_):
    buttons = [
        [
            InlineKeyboardButton(
                text=_["S_B_1"], url=f"https://t.me/{app.username}?startgroup=true"
            ),
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT, icon_custom_emoji_id=5247029067256987229),
        ],
    ]
    return buttons


def private_panel(_):
    buttons = [
        [
            InlineKeyboardButton(text=_["S_B_4"], callback_data="settings_back_helper", icon_custom_emoji_id=5818705028424141605),
        ],
        [
            InlineKeyboardButton(text=_["S_B_2"], url=config.SUPPORT_CHAT, icon_custom_emoji_id=5971867376130461576),
            InlineKeyboardButton(text=_["S_B_6"], url=config.SUPPORT_CHANNEL, icon_custom_emoji_id=5960842268096073715),
        ],
        [
            InlineKeyboardButton(
                text=_["S_B_3"],
                url=f"https://t.me/{app.username}?startgroup=true",
                icon_custom_emoji_id=6312260233171312151
            )
        ],
    ]
    return buttons
