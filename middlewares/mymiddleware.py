from aiogram import BaseMiddleware
from aiogram.types import Message,Update
from typing import *
# from utils.misc.checksub import joinchat
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
            from utils.misc.checksub import joinchat
            user_id = str(event.from_user.id)

            if event.text.startswith("/start"):
                user_commands[user_id] = '/start'
                return await handler(event, data)

            if event.text.startswith("/referal"):
                user_commands[user_id] = '/referal'

            if event.text.startswith("/topreferals"):
                user_commands[user_id] = '/topreferals'

            if event.text.startswith("/help"):
                return await handler(event, data)
            
            if user_id in ADMINS:
                return await handler(event, data)

            is_member = await joinchat(event.from_user.id)
            if not is_member:
                return

        return await handler(event, data)
