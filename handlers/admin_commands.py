from aiogram import Router, Bot
from aiogram.filters import Command
from aiogram.types import Message

from utils.interface import (get_all_accounts, ban_skin_by_username, unban_skin_by_username, ban_by_username, unban_by_username, 
                             get_account_by_username, real_delete_account_by_username, change_owner)
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


@rt.message(MenuStates.menu, AdminFilter(), Command("admin"))
async def cmd_admin_list(message: Message, bot: Bot):
    await message.answer(
"""Все доступные команды:
    • /ban_skin Ник Причина
    • /unban_skin Ник
    • /ban Ник Причина
    • /unban Ник
    • /delete_account Ник Причина
    • /change_owner Ник ID_нового_владельца
    
""")


@rt.message(MenuStates.menu, AdminFilter(), Command("ban_skin"))
async def cmd_ban_skin(message: Message, bot: Bot):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) < 2:
        await message.answer("Надо указать ник аккаунта и, опционально, причину")
        return
    
    _, username, *reason_list = args

    reason = " ".join(reason_list) or "*не указано*"
    
    success, msg = ban_skin_by_username(username, reason)
    if not success:
        await message.answer(f"Что-то не так при выдаче бана: {msg}")
        return

    await message.answer(f"Бан выдан")

    account = get_account_by_username(username)
    assert account is not None
    try: await bot.send_message(account.telegramID, f"Вашему аккаунту {username} заблокировали возможность менять скин по причине {reason}")
    except Exception: pass


@rt.message(MenuStates.menu, AdminFilter(), Command("unban_skin"))
async def cmd_unban_skin(message: Message, bot: Bot):
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

    account = get_account_by_username(username)
    assert account is not None
    try: await bot.send_message(account.telegramID, f"Ваш аккаунт {username} теперь может менять скин")
    except Exception: pass


@rt.message(MenuStates.menu, AdminFilter(), Command("ban"))
async def cmd_ban(message: Message, bot: Bot):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) < 2:
        await message.answer("Надо указать ник аккаунта и, опционально, причину")
        return
    
    _, username, *reason_list = args

    reason = " ".join(reason_list) or "*не указано*"
    
    success, msg = ban_by_username(username, reason)
    if not success:
        await message.answer(f"Что-то не так при выдаче бана: {msg}")
        return

    await message.answer(f"Бан выдан. Теперь игрок, имеющий аккаунт {username}, не сможет использовать бота.")

    account = get_account_by_username(username)
    assert account is not None
    try: await bot.send_message(account.telegramID, f"Вы были забанены по причине {reason}")
    except Exception: pass


@rt.message(MenuStates.menu, AdminFilter(), Command("unban"))
async def cmd_unban(message: Message, bot: Bot):
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

    account = get_account_by_username(username)
    assert account is not None

    await message.answer(f"Бан снят. Теперь игрок, имеющий аккаунт {username}, сможет использовать бота.")

    try: await bot.send_message(account.telegramID, "Вы были разбанены")
    except Exception: pass


@rt.message(MenuStates.menu, AdminFilter(), Command("delete_account"))
async def cmd_delete_account(message: Message, bot: Bot):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) < 2:
        await message.answer("Надо указать ник аккаунта и, опционально, причину")
        return
    
    _, username, *reason_list = args

    reason = " ".join(reason_list) or "*не указано*"

    account = get_account_by_username(username)
    assert account is not None
    
    success, msg = real_delete_account_by_username(username)
    if not success:
        await message.answer(f"Что-то не так при удалении аккаунта: {msg}")
        return

    await message.answer(f"Аккаунт {username!r} удалён")

    # try: await bot.send_message(account.telegramID, f"Ваш аккаунт {username!r} удалён по причине {reason}")
    # except Exception: pass


@rt.message(MenuStates.menu, AdminFilter(), Command("change_owner"))
async def cmd_change_owner(message: Message, bot: Bot):
    if message.from_user is None:
        return
    if message.text is None:
        return

    args = message.text.split(" ")

    if len(args) != 3:
        await message.answer("Надо указать ник аккаунта и ID нового хозяина акканунта")
        return
    
    _, username, new_id = args

    account = get_account_by_username(username)
    assert account is not None

    if not new_id.isdecimal():
        await message.answer("ID - не число.")
        return
    
    _new_id = int(new_id)

    success, msg = change_owner(username, _new_id)
    if not success:
        await message.answer(f"Что-то не так при передачи аккаунта: {msg}")
        return

    await message.answer(f"Аккаунт {username!r} успешно передан")