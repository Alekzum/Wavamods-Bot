from aiogram import Dispatcher
import os


def include_routers(dp: Dispatcher, root="handlers"):
    files = [x for x in os.listdir(root) if x.endswith(".py")]
    dp.include_routers(*[__import__(f'{root}.{file.removesuffix(".py")}', fromlist=('rt')).rt for file in files])