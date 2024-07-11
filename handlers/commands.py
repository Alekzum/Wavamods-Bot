from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext

from utils.interface import (
    get_accounts_by_uid, change_skin, get_account_count_by_uid, get_all_accounts, 
    get_account_by_username, get_usernames_by_uid, change_password, ban_skin_by_username, unban_skin_by_username
)
from utils.my_states import MenuStates, RegisterStates
from utils.my_checkers import AdminFilter, isAdmin, check_skin
import logging
import pathlib


splitter = "\n\n • "
logger = logging.getLogger(__name__)
rt = Router()
commands_are_changed = False


@rt.message(StateFilter(None), CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MenuStates.need_register)
    await message.answer("Здравствуйте! Для регистрации аккаунта, необходимо написать /register")

    global commands_are_changed
    if not commands_are_changed:
        await update_commands(message, bot)


@rt.message(CommandStart())
async def update_commands(message: Message, bot: Bot):
    global commands_are_changed
    if not commands_are_changed:
        await bot.set_my_commands(
            [
                BotCommand(command="register", description="Привязать ваш аккаунт телеграм к аккаунту майнкрафт"),
                BotCommand(command="skin", description="Установить скин"),
                BotCommand(command="cancel", description="Отменить текущее действие"),
                BotCommand(command="changepass", description="Изменить пароль от аккаунта"),
                BotCommand(command="profiles", description="Перечислить все ваши аккаунты"),
                BotCommand(command="profile", description="Получить информацию об вашем аккаунте"),
                BotCommand(command="privacy", description="Наша политика приватности")
            ]
        )
        commands_are_changed = True


@rt.message(StateFilter(MenuStates.need_register, MenuStates.menu), Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    
    account_count = get_account_count_by_uid(message.from_user.id)
    if account_count >= 3:
        await message.answer("Вы достигли лимита по количеству аккаунтов на одного человека. Максимум вы можете иметь 3 аккаунта.")
        return

    await message.answer("Напишите ник для вашего аккаунта (от 3 до 12 символов, только английские буквы и цифры)")
    await state.set_state(RegisterStates.input_username)


@rt.message(MenuStates.menu, Command("skin"))
async def cmd_skin(message: Message):
    if message.from_user is None or message.text is None:
        return
    
    uid = message.from_user.id

    args = message.text.split(" ")

    if len(args) in [1, 2]:
        await message.answer(
            "Вместе с командой введите ник вашего аккаунта и ссылку на ваш скин. "
            "Ссылка должна содержать изображение с одним из таких расширений: .png, .jpg, .jpeg"
            "Пример: /skin someone https://best.site.ever/some/path/skin.png"
        )
        return
    
    elif len(args) > 3:
        await message.answer(
            "Слишком много аргументов. "
            "Вместе с командой введите ник вашего аккаунта и ссылку на ваш скин. "
            "Ссылка должна содержать изображение с одним из таких расширений: .png, .jpg, .jpeg. "
            "Пример использования: /skin someone https://best.site.ever/some/path/skin.png"
        )
        return

    _, username, url = args

    accounts = get_accounts_by_uid(uid)
    if accounts is None:
        await message.answer("У вас нет аккаунтов")
        return
    
    usernames = [a.username for a in accounts]

    if username not in usernames:
        await message.answer("Аккаунта с таким ником нет среди ваших")
        return

    urlValid, msg = await check_skin(url)
    if not urlValid:
        await message.answer(f"Что-то пошло не так при проверке скина. Подробнее: {msg}")
        return

    account = accounts[usernames.index(username)]
    password = account.password

    status, msg = change_skin(username=username, password=password, skinURL=url)
    if not status:
        await message.answer(f"Что-то пошло не так при изменении скина. Подробнее: {msg}")
        return

    await message.answer("Скин успешно изменён")


@rt.message(MenuStates.menu, Command("profiles"))
async def cmd_profiles(message: Message, state: FSMContext):
    if message.from_user is None:
        return

    accounts = get_accounts_by_uid(message.from_user.id)
    if accounts is None:
        await message.answer(f"У вас нет аккаунтов")
        return

    accounts_string = [str(acc) for acc in accounts]
    result = splitter.join([""] + accounts_string)
    await message.answer(f"Все ваши аккаунты: {result}")


@rt.message(MenuStates.menu, Command("profile"))
async def cmd_profile(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    if message.text is None:
        return

    uid = message.from_user.id
    args = message.text.split(" ")

    if len(args) == 1 or len(args) > 2:
        await message.answer("Надо указать ник вашего аккаунта")
        return
    
    _, username = args
    
    usernames = get_usernames_by_uid(uid) or []
    if username not in usernames:
        await message.answer("У вас нет такого аккаунта")
        return
    
    account = get_account_by_username(username)
    if account is None:
        await message.answer(f"Аккаунта с таким ником нет")
        return
    
    text = str(account)
    await message.answer(text)


@rt.message(MenuStates.menu, Command("changepass"))
async def cmd_changepass(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    if message.text is None:
        return

    uid = message.from_user.id
    args = message.text.split(" ")

    if len(args) != 3:
        await message.answer("Надо указать ник вашего аккаунта и новый пароль для него")
        return
    
    _, username, password = args
    
    usernames = get_usernames_by_uid(uid) or []
    if username not in usernames:
        await message.answer("У вас нет такого аккаунта")
        return
    
    account = get_account_by_username(username)
    if account is None:
        await message.answer(f"Аккаунта с таким ником нет")
        return
    
    success, msg = change_password(username, account.password, password)
    if not success:
        await message.answer(f"Что-то не так при смене пароля: {msg}")
        return
    
    await message.answer("Пароль успешно изменён!")


@rt.message(Command("privacy"))
async def cmd_privacy(message: Message, bot: Bot):
    bot_me = await bot.me()
    bot_name = bot_me.username
    privacy_path = str(pathlib.Path("data/privacy.txt"))
    
    with open(privacy_path, encoding="utf-8") as f:
        privacy_text = f.read().format(bot_name=bot_name, support_name="faustyuz")

    await message.answer(privacy_text)


@rt.message(StateFilter(None), Command("cancel"))
async def cmd_cancel_in_start(message: Message):
    await message.answer("Как вы прописали команду /cancel раньше команды /start? o-0")

@rt.message(MenuStates.menu, Command("cancel"))
async def cmd_cancel_already_in_menu(message: Message):
    await message.answer("Нечего отменять, вы и так в меню")


@rt.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.set_state(MenuStates.menu)
    await message.answer("Хорошо. Вы теперь в меню. ")


# Admin's things


@rt.message(MenuStates.menu, AdminFilter(), Command("admin"))
async def cmd_admin(message: Message, state: FSMContext):
    accounts = get_all_accounts() or []
    ban_hint = "Можно убрать возможность менять скин у человека при помощи `/ban_skin ник [причина]`, или снять с помощью `/unban_skin ник`" \
        "\nАккаунты в базе данных:"

    results = [str(account) for account in accounts]
    text = ban_hint + (splitter.join([""] + results) if results else "  Никого нет в базе данных...")
    await message.answer(text)


@rt.message(MenuStates.menu, AdminFilter(), Command("ban_skin"))
async def cmd_ban_skin(message: Message, state: FSMContext):
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
async def cmd_unban_skin(message: Message, state: FSMContext):
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
