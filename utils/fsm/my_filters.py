from aiogram.types import CallbackQuery, Message
from aiogram.filters import BaseFilter
from ..config import ADMIN_IDS


class AdminFilter(BaseFilter):
    async def __call__(self, thing: Message|CallbackQuery) -> bool:
        return bool(thing.from_user and (thing.from_user.id in ADMIN_IDS))