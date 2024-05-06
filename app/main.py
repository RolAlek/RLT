import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient

from handlers.handlers import router
from middlewares.db import DbSessionMiddleware


load_dotenv('.env')

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')
    logger.info('Starting bot')

    client = AsyncIOMotorClient(os.environ['MONGO_DB_URL'])

    bot = Bot(token=os.environ['BOT_TOKEN'], parse_mode='HTML')
    dp = Dispatcher()
    dp.include_router(router)
    dp.update.middleware(DbSessionMiddleware(client))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
