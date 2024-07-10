from aiogram import Router, Bot
from aiogram.filters import Command, StateFilter, CommandStart
from aiogram.types import Message, BotCommand
from aiogram.fsm.context import FSMContext
from utils.interface import get_accounts_by_uid, change_skin, get_account_count_by_uid
from utils.my_states import MenuStates, RegisterStates
from http.client import responses
import aiohttp
import logging
import pathlib
import re


logger = logging.getLogger(__name__)
rt = Router()
commands_are_changed = False
url_validator = re.compile(r"https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256})\.([a-zA-Z0-9()]{1,6})\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\.(png|jpg|jpeg)")


@rt.message(StateFilter(None), CommandStart())
async def cmd_start(message: Message, bot: Bot, state: FSMContext):
    await state.set_state(MenuStates.menu)
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
                BotCommand(command="privacy", description="Наша политика приватности")
            ]
        )
        commands_are_changed = True


@rt.message(MenuStates.menu, Command("register"))
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

    usernames = [str(acc.username) for acc in accounts]
    result = "\n • ".join([""] + usernames)
    await message.answer(f"Все ваши аккаунты: {result}")


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


async def check_skin(skin_url) -> tuple[bool, str]:
    matched_url = url_validator.match(skin_url)
    if matched_url is None:
        return (False, "Ссылка неправильная. Попробуйте нормальную ссылку")
    
    try:
        async with aiohttp.ClientSession() as session: 
            async with session.get(skin_url) as response:
                status = response.status
    except Exception:
        return (False, "Ссылка неправильная. Попробуйте нормальную ссылку")

    if status == 429:
        return (False, f"Не могу загрузить скин. Попробуйте другую ссылку")
    
    elif status != 200:
        return (False, f"Не могу загрузить скин. Код ошибки: {responses[status]}. Попробуйте другую ссылку")

    return (True, "Ссылка правильная")
