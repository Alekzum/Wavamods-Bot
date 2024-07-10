from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from utils.my_states import MenuStates, RegisterStates, ChangeSkinStates
from utils.interface import add_user, user_is_exists
import logging
import re


logger = logging.getLogger(__name__)
rt = Router()

login_checker = re.compile(r"[a-zA-Z0-9]+")


@rt.message(RegisterStates.input_username)
async def fsm_register_username(message: Message, state: FSMContext):
    username = message.text

    if username is None:
        await message.answer("Текст в вашем сообщении не найден. Введите ваш ник")
        return
    
    elif len(username) < 3:
        await message.answer("Ник должен быть по-длиннее. Попробуйте другой ник")
        return
        
    elif len(username) > 12:
        await message.answer("Ник должен быть по-короче. Попробуйте другой ник")
        return
    
    elif login_checker.fullmatch(username) is None:
        await message.answer("Ваш ник состоит не только из английских букв и цифр. Попробуйте другой ник")
        return

    alredy_exists = user_is_exists(username)
    if alredy_exists:
        await message.answer("Данный ник уже занят. Попробуйте другой ник")
        return
    
    await state.update_data(dict(username=username))
    await state.set_state(RegisterStates.input_password)
    await message.answer(f"Хорошо, ваш ник {username}. Теперь нужно ввести пароль (от 6 символов).")


@rt.message(RegisterStates.input_password)
async def fsm_register_password(message: Message, state: FSMContext):
    if message.from_user is None:
        return 
    
    password = message.text

    if password is None:
        await message.answer("А где пароль?")
        return
    
    elif len(password) < 6:
        await message.answer("Пароль должен быть длиннее")
        return
    
    data = await state.get_data()
    username = data.get('username')
    if username is None:
        await message.answer("Что-то не так с логином. Пройдите регистрацию ещё раз с помощью команды /register.")
        await state.set_state()
        return

    status, msg = add_user(uid=message.from_user.id, username=username, password=password)
    if not status:
        await message.answer(f"Что-то пошло не так. Пройдите регистрацию ещё раз с помощью команды /register. Подробнее: {msg}")
        await state.clear()
        return
    
    await state.clear()

    await state.set_state(MenuStates.menu)
    await message.answer(f"Регистрация прошла успешно! По желанию можно поменять свой скин командой /skin")
