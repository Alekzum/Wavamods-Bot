from aiogram.filters import BaseFilter
from http.client import responses
import aiohttp
import re


url_validator = re.compile(r"https?:\/\/(www\.)?([-a-zA-Z0-9@:%._\+~#=]{1,256})\.([a-zA-Z0-9()]{1,6})\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)\.(png|jpg|jpeg)")
username_checker = re.compile(r"[a-zA-Z0-9]+")
password_checker = re.compile(r"\w+")


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


async def check_username(username: str) -> tuple[bool, str]:    
    if not username_checker.fullmatch(username):
        return (False, "Ваш ник состоит не только из английских букв и цифр. Попробуйте другой ник")

    elif len(username) < 3:
        return (False, "Ник должен быть по-длиннее. Попробуйте другой ник")
        
    elif len(username) > 12:
        return (False, "Ник должен быть по-короче. Попробуйте другой ник")
    
    return (True, "Ник правильный")


async def check_password(password: str) -> tuple[bool, str]:
    if not password_checker.fullmatch(password):
        return (False, "Пароль должен состоять только из букв английского алфавита, цифр, и символа _")
    
    elif len(password) < 6:
        return (False, "Пароль должен быть длиннее")
    
    return (True, "Пароль правильный")
