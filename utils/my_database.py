# from html.parser import escape, unescape
from .my_classes import Account
from typing import Optional
import sqlite3


DATABASE_PATH = "data/database.db"


with sqlite3.connect(DATABASE_PATH) as con:
    cur = con.cursor()
    cur.execute("""
CREATE TABLE IF NOT EXISTS Users(
    uid INTEGER,
    login STRING,
    password STRING,
    skin STRING,
    active INTEGER
)
""")
    con.commit()


def user_is_exists(login: str) -> bool:
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT skin FROM Users WHERE login = ?", (login, ))
        result: tuple[str] | None = cur.fetchone()
    return result is not None


def get_account_count_by_uid(uid: int) -> int:
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM Users WHERE uid=?", (uid, ))
        result: list[tuple] | None = cur.fetchall()
    return len(result) if result else 0


def get_accounts_by_uid(uid: int) -> list[Account] | None:
    """return list like [(uid, login1, password1, skin1), ((uid, login2, password2, skin2)), ((uid, login3, password3, skin3))]"""
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT uid, login, password, skin FROM Users WHERE uid=?", (uid, ))
        result: list[tuple[int, str, str, str]] | None = cur.fetchall()
    return [Account(*t) for t in result] if result else None


def get_user_by_uid_and_login(uid: int, login: str) -> Account | None:
    """return tuple like (uid, skin)"""
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT uid, login, password, skin FROM Users WHERE uid=? AND login=?", (uid, login, ))
        result: tuple[int, str, str, str] | None = cur.fetchone()
    return Account(*result) if result else None


def get_user_by_login_and_password(login: str, password: str) -> Account | None:
    """return tuple like (uid, skin)"""
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("SELECT uid, login, password, skin FROM Users WHERE login=? AND password=?", (login, password, ))
        result: tuple[int, str, str, str] | None = cur.fetchone()
    return Account(*result) if result else None


def add_user(uid: int, login: str, password: str, skin: Optional[str] = None) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    already_exists = user_is_exists(login)
    if already_exists:
        return (False, "Данный ник занят")

    if skin is None:
        skin = ""
        
    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Users (uid, login, password, skin) VALUES (?, ?, ?, ?)", (uid, login, password, skin, ))
        con.commit()
    
    return (True, "Пользователь добавлен в базу данных")


def change_skin(uid: int, login: str, password: str, skin: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = get_user_by_login_and_password(login, password)
    if user is None:
        return (False, "Данного логина нет в базе данных")
    
    elif user.password != password:
        return (False, "Пароль неправильный")

    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("UPDATE Users SET skin = ? WHERE login = ?", (skin, login, ))
        con.commit()
    
    return (True, "Скин пользователя обновлён")


def delete_user(login: str, password: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = get_user_by_login_and_password(login, password)
    if user is None:
        return (False, "Данного логина нет в базе данных")
    
    elif user.password != password:
        return (False, "Пароль неправильный")

    with sqlite3.connect(DATABASE_PATH) as con:
        cur = con.cursor()
        cur.execute("DELETE FROM Users WHERE login = ?", (login, ))
        con.commit()

    return True, "Пользователь удалён из базы данных"


# def change_uid(old_uid: int, login: str, password: str, new_uid: int) -> tuple[bool, str]:
#     """return tuple like (status, message)"""
#     # Пусть будет, вдруг захотите добавить...
#     user = get_user_by_login_and_password(login, password)
#     if user is None:
#         return (False, "Данного логина нет в базе данных")
    
#     elif user[0] != old_uid:
#         return (False, "Прошлый ID неверный")
    
#     elif user[2] != password:
#         return (False, "Пароль неправильный")

#     with sqlite3.connect(DATABASE_PATH) as con:
#         cur = con.cursor()
#         cur.execute("UPDATE Users SET uid = ? WHERE login = ?, password = ?", (new_uid, login, password, ))
#         con.commit()
    
#     return (True, "ID пользователя обновлён")


if __name__ == "__main__":
    uid, login, password = 1337, "Alekzum", "wqvQotGLINC00YPQvNCw0Lsg0YLRg9GCINGH0YLQvi3RgtC+INCx0YPQtNC10YI/wrs"

    is_exists = user_is_exists(login)
    print(f"{is_exists=}")
    
    user = add_user(uid, login, password)
    print(user)

    is_exists = user_is_exists(login)
    print(f"{is_exists=}")
    
    result = change_skin(uid, login, password, "https://habr.com/ru/articles/754400/")
    print(result)

    is_exists = user_is_exists(login)
    print(f"{is_exists=}")

    result = delete_user(login, password)
    print(result)

    is_exists = user_is_exists(login)
    print(f"{is_exists=}")
