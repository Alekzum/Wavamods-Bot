from utils.config import RCON_HOST, RCON_PORT, RCON_PASSWORD, STUPIDWALLET_TOKEN, SUPPORT_NAME
from utils import my_database
from mcrcon import MCRcon  # type: ignore[import-untyped]
from stupidwallet import Wallet  # type: ignore[import-untyped]

from aiogram.fsm.context import FSMContext

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardButton

from aiogram.filters import Command, CommandStart
from aiogram.types import Message, BotCommand
from aiogram import Router, Bot
import asyncio
import logging

import os


logger = logging.getLogger(__name__)
rt = Router(name=__name__)
# rcon = Client(host=RCON_HOST, port=RCON_PORT, passwd=RCON_PASSWORD)
wallet = Wallet(STUPIDWALLET_TOKEN)

COIN_ID = 2
COIN_AMOUNT = 1
COIN_NAME = {1:"WAV",2:"TWAV"}[COIN_ID]
COIN_DISPLAYNAME = f"{COIN_AMOUNT} {COIN_NAME}"

commands_are_changed = False


async def append_text(msg: Message, text: str, **kwargs) -> Message:
    result = await msg.edit_text(msg.html_text + "\n\n" + text, **kwargs)
    assert isinstance(result, Message), "wth"
    return result


@rt.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    await message.answer(f"Здравствуйте! Для добавления аккаунта в белый список, необходимо написать `/add_user ваш_ник`, и заплатить {COIN_DISPLAYNAME}")
    
    global commands_are_changed
    if not commands_are_changed:
        await bot.set_my_commands(
            [
                BotCommand(command="add_user", description="Добавить аккаунт в белый список сервера майнкрафт"),
                BotCommand(command="profiles", description="Перечислить все ваши аккаунты"),
                BotCommand(command="privacy", description="Наша политика приватности")
            ]
        )
        commands_are_changed = True


@rt.message(Command("add_user"))
async def cmd_add_user(message: Message, bot: Bot, state: FSMContext):
    if message.text is None: return
    elif message.from_user is None: return
    args = message.text.split(" ")
    if len(args) != 2: return await message.answer("Вам надо указать ник своего аккаунта вместе с командой. Например: /add_user SuperKrutayaTyan")
    command, username = args

    isExists = my_database.accountIsExists(username)
    if isExists: return await message.answer("Данный аккаунт уже в белом списке.")
    _msg = await message.answer(f"Что бы добавить свой аккаунт на сервер, вам нужно заплатить {COIN_DISPLAYNAME}. Создаётся счёт...")
    
    me = await bot.me()
    await check_expired_invoices(wallet)
    invoice = await wallet.create_invoice(COIN_ID, COIN_AMOUNT, comment="За добавление своего аккаунта", return_url=f"https://t.me/{me.username}")
    keyboard = InlineKeyboardBuilder([[InlineKeyboardButton(text=COIN_DISPLAYNAME, url=invoice.url)]]).as_markup()

    _msg = await _msg.edit_text(f"Вот счёт на {COIN_DISPLAYNAME}, который нужно оплатить", reply_markup=keyboard)  # type: ignore[assignment]

    payed = await wallet.wait_pay_invoice(invoice.invoice_unique_hash)
    await wallet.delete_invoice(invoice.invoice_unique_hash)
    if payed is None: return await append_text(_msg, "Счёт не создался...")
    elif not payed: return [await append_text(_msg, "Вы не оплатили счёт.")]
    _msg = await _msg.edit_text("Оплата получена!")  # type: ignore[assignment]

    _msg = await append_text(_msg, "Отправлен запрос на добавление аккаунта в белый список...")  # type: ignore[assignment]

    command = f"whitelist add {username}"
    try:
        with MCRcon(host=RCON_HOST, password=RCON_PASSWORD, port=RCON_PORT) as mcr:
            response = mcr.command(command)
    except Exception as ex:
        response = f"Произошла ошибка при отправке запроса: {ex!r}\n\nСоздаётся чек, что бы вернуть средства..."
        _msg = await append_text(_msg, response)
        cheque = await wallet.create_cheque(COIN_ID, COIN_AMOUNT, comment="Создателю бота жаль, что так случилось")
        keyboard = InlineKeyboardBuilder([[InlineKeyboardButton(text=COIN_DISPLAYNAME, url=cheque.url)]]).as_markup()
        return await append_text(_msg, f"Вот чек с {COIN_DISPLAYNAME}", reply_markup=keyboard)
    
    if response == "Player is already whitelisted":
        my_database.removeAccount(message.from_user.id, username)
        success, msg = my_database.addAccount(message.from_user.id, username)
        _msg = await append_text(_msg, f"Ответ от сервера: {response!r}\n\nСоздаётся чек, что бы вернуть средства...")
        cheque = await wallet.create_cheque(COIN_ID, COIN_AMOUNT, comment="")
        keyboard = InlineKeyboardBuilder([[InlineKeyboardButton(text=COIN_DISPLAYNAME, url=cheque.url)]]).as_markup()
        return await append_text(_msg, f"Вот чек с {COIN_DISPLAYNAME}", reply_markup=keyboard)
    
    _msg = await append_text(_msg, f"Ответ от сервера: {response!r}\n\nДобавление аккаунта в локальный белый список...")
    success, msg = my_database.addAccount(message.from_user.id, username)
    if not success: return await append_text(_msg, f"Что-то пошло не так при добавлении аккаунта в локальный белый список: {msg}")
    _msg = await append_text(_msg, f"Аккаунт с ником {username!r} теперь в белом списке")


@rt.message(Command("privacy"))
async def cmd_privacy(message: Message, bot: Bot):
    bot_me = await bot.me()
    bot_name = bot_me.username
    privacy_path = os.sep.join(["data", "privacy.txt"])
    
    with open(privacy_path, encoding="utf-8") as f:
        privacy_text = f.read().format(bot_name=bot_name, support_name=SUPPORT_NAME)

    await message.answer(privacy_text)


_lock = False
_checked = False
async def check_expired_invoices(wallet: Wallet):
    global _lock
    global _checked
    
    while _lock:
        await asyncio.sleep(5)
    
    if _checked:
        return

    _lock = True
    await wallet.check_expired_invoices()
    _checked = True
    _lock = False

    return