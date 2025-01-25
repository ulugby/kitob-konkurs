import handlers.setup_handlers
import handlers,middlewares
from loader import dp,bot
from aiogram.types.bot_command_scope_all_private_chats import BotCommandScopeAllPrivateChats
import asyncio
from utils.notify_admins import start,shutdown
from utils.set_botcommands import commands
from middlewares.mymiddleware import UserCheckMiddleware
# Info
import logging
import sys

# from handlers.setup_handlers import setup_handlers
async def main():
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await bot.set_my_commands(commands=commands,scope=BotCommandScopeAllPrivateChats(type='all_private_chats'))

        # setup_handlers(dp)

        dp.startup.register(start)
        dp.shutdown.register(shutdown)
        dp.message.middleware(UserCheckMiddleware())
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
if __name__=='__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())