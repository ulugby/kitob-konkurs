from aiogram.filters import BaseFilter
from aiogram import types
from loader import bot

class IsBotAdmin(BaseFilter):
    
    async def __call__(self, message: types.Message) -> bool:
        mybot = await bot.get_chat_member(chat_id=message.chat.id,user_id=bot.id)
        return mybot.status.ADMINISTRATOR
