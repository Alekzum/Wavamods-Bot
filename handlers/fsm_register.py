from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from utils.my_checkers import check_username, check_password
from utils.fsm.my_states import MenuStates, RegisterStates
from utils.interface import add_account, account_is_exists
import logging


cancel_hint = "\nЕсли хотите отменить текущее действие, используйте команду /cancel"
logger = logging.getLogger(__name__)
rt = Router()


@rt.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.set_state(MenuStates.menu)
    await message.answer("Хорошо. Вы теперь в меню. ")


@rt.message(RegisterStates.input_username)
async def fsm_register_username(message: Message, state: FSMContext):
    username = message.text

    if username is None:
        await message.answer("Текст в вашем сообщении не найден. Введите ваш ник")
        return

    success, msg = await check_username(username)
    if not success:
        await message.answer(msg)
        return

    alredy_exists = account_is_exists(username)
    if alredy_exists:
        await message.answer("Данный ник уже занят. Попробуйте другой ник")
        return
    
    await state.update_data(dict(username=username))
    await state.set_state(RegisterStates.input_password)
    await message.answer(f"Хорошо, ваш ник {username}. Теперь нужно ввести пароль (от 6 символов)." + cancel_hint)


@rt.message(RegisterStates.input_password)
async def fsm_register_password(message: Message, state: FSMContext):
    if message.from_user is None:
        return 
    
    password = message.text

    if password is None:
        await message.answer("А где пароль?")
        return
    
    success, msg = await check_password(password)
    if not success:
        await message.answer(msg)
        return

    data = await state.get_data()
    username = data.get('username')
    if username is None:
        await message.answer("Что-то не так с логином. Пройдите регистрацию ещё раз с помощью команды /register.")
        await state.set_state(MenuStates.need_register)
        return

    status, msg = add_account(uid=message.from_user.id, username=username, password=password)
    if not status:
        await message.answer(f"Что-то пошло не так. Пройдите регистрацию ещё раз с помощью команды /register. Подробнее: {msg}")
        await state.set_state(MenuStates.need_register)
        return
    
    await state.clear()

    await state.set_state(MenuStates.menu)
    await message.answer(f"Регистрация прошла успешно! По желанию можно поменять свой скин командой /skin")
