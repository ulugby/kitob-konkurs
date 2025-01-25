from aiogram.filters import Command
from loader import dp,bot
from aiogram import types,html
from aiogram.types.reaction_type_emoji import ReactionTypeEmoji
import random

from aiogram.types import  InlineKeyboardButton,InlineKeyboardMarkup

@dp.message(Command('help'))
async def help_bot(message:types.Message):


    reaction_list = ["👨‍💻", "👀", "✍","🫡","⚡"]
    try:
        await bot.set_message_reaction(
            chat_id=message.chat.id,
            message_id=message.message_id,
            reaction=[ReactionTypeEmoji(emoji=random.choice(reaction_list))],
            is_big=False
        )
    except:
        pass
    await message.answer(
        "Sizga qanday yordam kerak? Agar bot ishlashida muammo bo'lsa bizga muroajat qiling",
        reply_markup=InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="Dasturchi 🧑🏻‍💻", url="tg://user?id=2083239343")]
            ]
        )
    )