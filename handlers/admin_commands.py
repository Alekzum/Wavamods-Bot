from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from utils.interface import get_all_accounts, ban_skin_by_username, unban_skin_by_username, ban_by_username, unban_by_username
from utils.fsm.my_states import MenuStates
from utils.fsm.my_filters import AdminFilter
import logging


cancel_hint = "\nЕсли хотите отменить текущее действие, используйте команду /cancel"
splitter = "\n\n • "
logger = logging.getLogger(__name__)
rt = Router()


@rt.message(MenuStates.menu, AdminFilter(), Command("admin"))
async def cmd_admin(message: Message):
    accounts = get_all_accounts() or []
    ban_hint = "Можно удалить аккаунт с помощью `/delete_account ник`\n\
Можно убрать возможность менять скин у человека при помощи `/ban_skin ник [причина]`, или снять с помощью `/unban_skin ник`\n\
Аккаунты в базе данных:"

    results = [str(account) for account in accounts]
    text = ban_hint + (splitter.join([""] + results) if results else "  Никого нет в базе данных...")
    await message.answer(text)
    


@rt.message(MenuStates.menu, AdminFilter(), Command("ban_skin"))
async def cmd_ban_skin(message: Message):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) < 2:
        await message.answer("Надо указать ник аккаунта и причину")
        return
    
    _, username, *reason_list = args

    if reason_list:
        reason = " ".join(reason_list)
    else:
        reason = None
    
    success, msg = ban_skin_by_username(username, reason)
    if not success:
        await message.answer(f"Что-то не так при выдаче бана: {msg}")
        return
    
    await message.answer(f"Бан выдан")


@rt.message(MenuStates.menu, AdminFilter(), Command("unban_skin"))
async def cmd_unban_skin(message: Message):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) != 2:
        await message.answer("Надо указать ник аккаунта")
        return
    
    _, username = args
    
    success, msg = unban_skin_by_username(username)
    if not success:
        await message.answer(f"Что-то не так при снятии бана: {msg}")
        return

    await message.answer(f"Бан снят")


@rt.message(MenuStates.menu, AdminFilter(), Command("ban"))
async def cmd_ban(message: Message):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) <= 2:
        await message.answer("Надо указать ник аккаунта и причину")
        return
    
    _, username, *reason_list = args

    reason = " ".join(reason_list)
    
    success, msg = ban_by_username(username)
    if not success:
        await message.answer(f"Что-то не так при выдаче бана: {msg}")
        return

    await message.answer(f"Бан выдан. Теперь игрок, имеющий аккаунт {username}, не сможет использовать бота.")


@rt.message(MenuStates.menu, AdminFilter(), Command("unban"))
async def cmd_unban(message: Message):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) != 2:
        await message.answer("Надо указать ник аккаунта")
        return
    
    _, username = args
    
    success, msg = unban_by_username(username)
    if not success:
        await message.answer(f"Что-то не так при снятии бана: {msg}")
        return

    await message.answer(f"Бан снят. Теперь игрок, имеющий аккаунт {username}, сможет использовать бота.")
