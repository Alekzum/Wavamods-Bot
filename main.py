import pathlib
import os


parent_directory = pathlib.Path(__file__)
# print(f"File's path is {parent_directory}")

# print(f"Change working directory to {parent_directory.parent}")
os.chdir(parent_directory.parent)


from utils.config import TOKEN, FSM_PATH
from utils.my_routers import include_routers
from utils.middleware import CooldownMiddleware
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
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="html"))
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
