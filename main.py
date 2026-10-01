import asyncio
import logging
from aiogram import Bot, Dispatcher
from config import config
from handlers.user_handlers import user_private_router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from database.database import async_session_maker
from middlewares.db import DbSessionMiddleware

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.tg_bot.token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

dp.update.outer_middleware(DbSessionMiddleware(session_pool=async_session_maker))
dp.include_router(user_private_router)

async def main():
    print('Бот успешно запущен!')
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот остановлен!')