from aiogram import Dispatcher, Bot
from aiogram.types import User
import asyncio
import os


def include_routers(dp: Dispatcher, root="handlers"):
    files = [x for x in os.listdir(root) if x.endswith(".py")]
    dp.include_routers(*[__import__(f'{root}.{file.removesuffix(".py")}', fromlist=('rt')).rt for file in files])


async def pooling(dp: Dispatcher, bot: Bot, polling_timeout: int = 30) -> None:
    """My implementation of Dispatcher._pooling"""
    user: User = await bot.me()
    print(f"Запущен бот @{user.username} id={bot.id} - {user.full_name}")
    try:
        async for update in dp._listen_updates(bot, polling_timeout=polling_timeout):
            handle_update = dp._process_update(bot=bot, update=update)
            
            handle_update_task = asyncio.create_task(handle_update)
            dp._handle_update_tasks.add(handle_update_task)
            handle_update_task.add_done_callback(dp._handle_update_tasks.discard)
    finally:
        print(f"Остановлен бот @{user.username} id={bot.id} - {user.full_name}")
