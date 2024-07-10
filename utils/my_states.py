from aiogram.fsm.state import StatesGroup, State


class MenuStates(StatesGroup):
    menu = State()


class RegisterStates(StatesGroup):
    input_username = State()
    input_password = State()
