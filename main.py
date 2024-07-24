from utils.runtime_platform import check_platform, in_venv


inVenv = in_venv()
# print(f"main.py started {'' if inVenv else 'not'} in venv")
check_platform()


from contextlib import suppress
from utils.config import BOT_TOKEN, FSM_PATH
from utils.my_functions import include_routers, pooling
from utils.my_middleware import CooldownMiddleware
from aiogram_sqlite_storage.sqlitestore import SQLStorage  # type: ignore
from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher
import asyncio


dp = Dispatcher(storage=SQLStorage(FSM_PATH))
include_routers(dp)

dp.message.middleware(CooldownMiddleware(1))


async def main():
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode="html"))
    print("Starting bot...")

    with suppress(KeyboardInterrupt, asyncio.exceptions.CancelledError):
        await pooling(dp, bot)

    print("Bot is stopped.")

if __name__ == "__main__":
    asyncio.run(main())
