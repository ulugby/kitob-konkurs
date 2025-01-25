from aiogram import BaseMiddleware
from aiogram.types import Message,Update
from typing import *
from utils.misc.checksub import joinchat
from data.config import ADMINS

from .user_commands import user_commands

class UserCheckMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any]
    ) -> Any:
    
        if isinstance(event, Message):
            user_id = str(event.from_user.id)
            
            # tekshirish uchun print qo'shamiz
            print("Received text:", event.text)

            if event.text.startswith("/topreferals"):
                user_commands[user_id] = '/topreferals'
                print("User command topreferals saved")

            if event.text.startswith("/referal"):
                user_commands[user_id] = '/referal'
                print("User command referal saved")

            if event.text.startswith("/start"):
                return await handler(event, data)
            
            if event.text.startswith("/help"):
                return await handler(event, data)
            
            if user_id in ADMINS:
                return await handler(event, data)

            is_member = await joinchat(event.from_user.id)
            if not is_member:
                return
        
        print("Current user_commands state:", user_commands)  # Tekshirish
        return await handler(event, data)
