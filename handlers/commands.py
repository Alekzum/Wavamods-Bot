from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext

from utils.fsm.my_states import MenuStates, RegisterStates
from utils.my_checkers import check_password, check_username
from utils import interface
import logging
import pathlib


cancel_hint = "\nЕсли хотите отменить текущее действие, используйте команду /cancel"
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
async def update_commands(_: Message, bot: Bot):
    global commands_are_changed
    if not commands_are_changed:
        await bot.set_my_commands(
            [
                BotCommand(command="cancel", description="Отменить текущее действие"),
                BotCommand(command="register", description="Привязать ваш аккаунт телеграм к аккаунту майнкрафт"),
                BotCommand(command="changepass", description="Изменить пароль от аккаунта"),
                BotCommand(command="profiles", description="Перечислить все ваши аккаунты"),
                BotCommand(command="admin", description="Если вы админ - показать все админ-команды"),
                # BotCommand(command="profile", description="Получить информацию об вашем аккаунте"),
                BotCommand(command="privacy", description="Наша политика приватности")
            ]
        )
        commands_are_changed = True


@rt.message(StateFilter(MenuStates.need_register, MenuStates.menu), Command("register"))
async def cmd_register(message: Message, state: FSMContext):
    if message.from_user is None:
        return
    elif message.text is None:
        return
    
    success, account_count = interface.get_account_count_by_uid(message.from_user.id)
    if not success: return await message.answer(f"При проверке что-то пошло не так. Подробнее: {account_count}")
    elif account_count >= 3:  # type: ignore[operator]  # mypy, you are the best
        await message.answer("Вы достигли лимита по количеству аккаунтов на одного человека. Максимум вы можете иметь 3 аккаунта.")
        return

    args = message.text.split(" ")
    if len(args) == 1:
        await message.answer("Напишите ник для вашего аккаунта (от 3 до 12 символов, только английские буквы и цифры)" + cancel_hint)
        await state.set_state(RegisterStates.input_username)
        return
    elif len(args) != 3: return await message.answer("Вы можете сразу зарегистрировать аккаунт, вписав ник и пароль для вашего аккаунта. Например: /register altuha superkrutaya")
    
    _, username, password = args

    success, msg = await check_username(username)
    if not success: return await message.answer(f"При проверке что-то пошло не так. Подробнее: {msg}")

    success, already_exists = interface.account_is_exists(username)
    if not success: return await message.answer(f"При проверке что-то пошло не так. Подробнее: {already_exists}")
    elif already_exists: return await message.answer("Данный ник уже занят. Попробуйте другой ник")
    
    success, msg = await check_password(password)
    if not success: return await message.answer(f"При проверке что-то пошло не так. Подробнее: {msg}")

    success, msg = interface.add_account(uid=message.from_user.id, username=username, password=password)
    if not success:
        await message.answer(f"Что-то пошло не так. Пройдите регистрацию ещё раз с помощью команды /register. Подробнее: {msg}")
        await state.set_state(MenuStates.need_register)
        return
    
    await state.clear()

    await state.set_state(MenuStates.menu)
    await message.answer(f"Регистрация прошла успешно!")


@rt.message(MenuStates.menu, Command("profiles"))
async def cmd_profiles(message: Message):
    if message.from_user is None:
        return

    success, accounts = interface.get_accounts_by_uid(message.from_user.id)
    if not success: return await message.answer(f"Что-то пошло не так при получении аккаунтов: {accounts}")
    if accounts is None: return await message.answer(f"У вас нет аккаунтов")

    _accounts: list[str] = [""] + [str(acc) for acc in accounts]
    if not accounts:
        await message.answer("У вас нет аккаунтов.")
        return
    
    accounts_string = splitter.join(_accounts)
    await message.answer(f"Все ваши аккаунты: {accounts_string}\n\n\nВнимание! Ваши пароли зашифрованы. Если вы забыли пароль, "
                          "то можете поменять его командой /changepass аккаунт новый_пароль")

@rt.message(MenuStates.menu, Command("changepass"))
async def cmd_changepass(message: Message):
    if message.from_user is None:
        return
    if message.text is None:
        return

    uid = message.from_user.id
    args = message.text.split(" ")

    if len(args) != 3: return await message.answer("Надо указать ник вашего аккаунта и новый пароль для него")
    
    _, username, password = args
    
    success, usernames = interface.get_usernames_by_uid(uid)
    if not success: return await message.answer(f"Что-то пошло не так при получении ников: {usernames}")
    elif username not in (usernames or []): return await message.answer("У вас нет такого аккаунта")
    
    success, account = interface.get_account_by_username(username)
    if not success: return await message.answer(f"Что-то пошло не так при получении ников: {account}")
    elif account is None: return await message.answer(f"Аккаунта с таким ником нет")

    success, msg = await check_password(password)
    if not success: return await message.answer(f"Что-то пошло не так при проверке пароля: {msg}")
    
    success, msg = interface.change_password(username, password)
    if not success: return await message.answer(f"Что-то пошло не так при смене пароля: {msg}")
    
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