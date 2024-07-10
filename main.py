from utils.config import BOT_TOKEN, FSM_PATH
from utils.my_routers import include_routers
from utils.my_middleware import CooldownMiddleware
from aiogram_sqlite_storage.sqlitestore import SQLStorage  # type: ignore
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
import asyncio
import pathlib


dp = Dispatcher(storage=SQLStorage(FSM_PATH))
include_routers(dp)

dp.message.middleware(CooldownMiddleware(1))
dp.callback_query.middleware(CooldownMiddleware(10))


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="html"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
