from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext

from utils.interface import get_accounts_by_uid, change_skin, get_account_count_by_uid, get_account_by_username, get_usernames_by_uid, change_password
from utils.fsm.my_states import MenuStates, RegisterStates
from utils.my_checkers import check_skin, check_password
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
                BotCommand(command="skin", description="Установить скин"),
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
    
    account_count = get_account_count_by_uid(message.from_user.id)
    if account_count >= 3:
        await message.answer("Вы достигли лимита по количеству аккаунтов на одного человека. Максимум вы можете иметь 3 аккаунта.")
        return

    await message.answer("Напишите ник для вашего аккаунта (от 3 до 12 символов, только английские буквы и цифры)" + cancel_hint)
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

    status, msg = change_skin(username=username, skinURL=url)
    if not status:
        await message.answer(f"Что-то пошло не так при изменении скина. Подробнее: {msg}")
        return

    await message.answer("Скин успешно изменён")


@rt.message(MenuStates.menu, Command("profiles"))
async def cmd_profiles(message: Message):
    if message.from_user is None:
        return

    accounts = get_accounts_by_uid(message.from_user.id)
    if accounts is None:
        await message.answer(f"У вас нет аккаунтов")
        return

    accounts_string = [str(acc) for acc in accounts]
    result = splitter.join([""] + accounts_string)
    await message.answer(f"Все ваши аккаунты: {result}.\n\n\nВнимание! Ваши пароли зашифрованы. Если вы забыли пароль, "
                         "то можете поменять его командой /changepass аккаунт новый_пароль")


@rt.message(MenuStates.menu, Command("changepass"))
async def cmd_changepass(message: Message):
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

    success, msg = await check_password(password)
    if not success:
        await message.answer(msg)
        return
    
    success, msg = change_password(username, password)
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