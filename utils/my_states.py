from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    need_register = State()
    menu = State()


class RegisterStates(StatesGroup):
    input_username = State()
    input_password = State()
