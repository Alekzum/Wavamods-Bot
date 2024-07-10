# from html.parser import escape, unescape
from ..config import DB_IP, DB_NAME, DB_LOGIN, DB_PASSWORD
from ..my_classes import Account
from typing import Optional, TypedDict
import pymysql.cursors  # type: ignore
import pymysql  # type: ignore
import logging


TABLE_NAME = "users"
logger = logging.getLogger(__name__)

class ACCOUNT_TUPLE(TypedDict):
    username: str
    password: str
    skinURL: str

# with connect_to_database() as con:
#     cur = con.cursor()
#     cur.execute("""
# CREATE TABLE IF NOT EXISTS `{TABLE_NAME}`(
#     uid INTEGER,
#     username STRING,
#     password STRING,
#     skinURL STRING,
#     active INTEGER
# )
# """)
#     con.commit()


def connect_to_remote_database():
    connection = pymysql.connect(
        database=DB_NAME, host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def userIsExists(username: str) -> bool:
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `skinURL` FROM `{TABLE_NAME}` WHERE `username`=%s", (username, ))
            result: tuple[str] | None = cur.fetchone()
    return result is not None


def getAccountCountByUid(uid: int) -> int:
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE `uid`=%s", (uid, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return len(result) if result else 0


def getAccountsByUid(uid: int) -> list[Account] | None:
    """return list like [Account1, Account2, Account3]"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL` FROM `{TABLE_NAME}` WHERE `uid`=%s", (uid, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return [Account(**t) for t in result] if result else None


def getUserByUsername(username: str) -> Account | None:
    """return tuple like (password, skinURL)"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL` FROM `{TABLE_NAME}` WHERE `username`=%s", (username, ))
            result: ACCOUNT_TUPLE | None = cur.fetchone()
    return Account(**result) if result else None


def addUser(uid: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    already_exists = userIsExists(username)
    if already_exists:
        return (False, "Данный ник занят")

    if skinURL is None:
        skinURL = ""
        
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE_NAME}` (`username`, `password`, `skinURL`) VALUES (%s, %s, %s)", (username, password, skinURL, ))
            con.commit()
    
    return (True, "Пользователь добавлен в базу данных")


def changeSkin(uid: int, username: str, password: str, skinURL: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = getUserByUsername(username)
    if user is None:
        return (False, "Данного логина нет в базе данных")
    
    elif user.password != password:
        logger.info(f"Except {user.password!r}, get {password!r}")
        return (False, "Пароль неправильный")

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET skinURL=%s WHERE `username`=%s", (skinURL, username, ))
            con.commit()
    
    return (True, "Скин пользователя обновлён")


def deleteUser(username: str, password: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = getUserByUsername(username)
    if user is None:
        return (False, "Данного логина нет в базе данных")
    
    elif user.password != password:
        logger.info(f"Except {user.password!r}, get {password!r}")
        return (False, "Пароль неправильный")

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"DELETE FROM `{TABLE_NAME}` WHERE `username`=%s", (username, ))
            con.commit()

    return True, "Пользователь удалён из базы данных"
