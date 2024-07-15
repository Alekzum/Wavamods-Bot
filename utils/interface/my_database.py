# from html.parser import escape, unescape
from ..config import DB_IP, DB_NAME, DB_LOGIN, DB_PASSWORD
from ..my_classes import Account
from typing import Optional, TypedDict, Literal, Any
import pymysql.cursors  # type: ignore
import pymysql  # type: ignore
import logging


TABLE_NAME = "users"
logger = logging.getLogger(__name__)


ErrorUsernameNotFound = (False, "Данного логина нет в базе данных")
ErrorPasswordIsWrong = (False, "Пароль неправильный")


class ACCOUNT_TUPLE(TypedDict):
    username: str
    password: str
    skinURL: str
    skinBanned: bool
    skinBannedReason: Optional[str]
    telegramID: int


def handle_pymysql_errors(func):
    def inner(*args, **kwargs) -> Any | tuple[Literal[False], str]:
        try:
            return func(*args, **kwargs)
        except pymysql.err.Error as ex:
            logger.error(repr(ex))
            return (False, "Произошла ошибка.")
    return inner


def connect_to_remote_database():
    connection = pymysql.connect(
        database=DB_NAME, host=DB_IP, user=DB_LOGIN, password=DB_PASSWORD, cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def accountIsExists(username: str) -> bool:
    temp_result = [a.username.lower() for a in (getAllAccounts() or [])]
    return username.lower() in temp_result


def getAccountCountByUid(telegramID: int) -> int:
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE `telegramID`=%s", (telegramID, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return len(result) if result else 0


def getAccountsByUid(telegramID: int) -> list[Account] | None:
    """return list like [Account1, Account2, Account3]"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}` WHERE `telegramID`=%s", (telegramID, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return [Account(**t) for t in result] if result else None


def getAllAccounts() -> list[Account] | None:
    """return list like [Account1, Account2, Account3]"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}`", ())
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return [Account(**t) for t in result] if result else None


def getAccountByUsername(username: str) -> Account | None:
    """return tuple like (password, skinURL)"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}` WHERE `username`=%s", (username, ))
            result: ACCOUNT_TUPLE | None = cur.fetchone()
    return Account(**result) if result else None


@handle_pymysql_errors
def addUser(telegramID: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    already_exists = accountIsExists(username)
    if already_exists:
        return (False, "Данный ник занят")

    if skinURL is None:
        skinURL = ""
        
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE_NAME}` (`username`, `password`, `skinURL`, `telegramID`) VALUES (%s, %s, %s, %s)", (username, password, skinURL, telegramID, ))
            con.commit()
    
    return (True, "Пользователь добавлен в базу данных")


@handle_pymysql_errors
def changeSkin(username: str, password: str, skinURL: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = getAccountByUsername(username)
    if user is None:
        return ErrorUsernameNotFound
    
    elif user.password != password:
        return ErrorPasswordIsWrong

    elif user.skinBanned:
        return (False, "Аккаунту запрещено менять скин. Причина: " + (user.skinBannedReason or "*Не указано*"))

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET skinURL=%s WHERE `username`=%s", (skinURL, username, ))
            con.commit()
    
    return (True, "Скин пользователя обновлён")


@handle_pymysql_errors
def changePassword(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    """return tuple like (status, message)"""
    user = getAccountByUsername(username)
    if user is None:
        return ErrorUsernameNotFound
    
    elif user.password != old_password:
        return ErrorPasswordIsWrong

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET password=%s WHERE `username`=%s", (new_password, username, ))
            con.commit()
    
    return (True, "Пароль пользователя обновлён")


@handle_pymysql_errors
def banSkinByUsername(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    account = getAccountByUsername(username)
    if account is None:
        return ErrorUsernameNotFound

    elif account.skinBanned:
        return (False, "Аккаунту уже запрещено менять скин")

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET `skinBanned`=1, `skinBannedReason`=%s WHERE `username`=%s", (username, reason or ""))
            con.commit()
    
    return (True, "Возможность аккаунта менять скин теперь заблокирована")


@handle_pymysql_errors
def deleteAccountByUsername(username: str) -> tuple[bool, str]:
    account = getAccountByUsername(username)
    if account is None:
        return ErrorUsernameNotFound

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET `telegramID`=1415937101, `skinURL`='' WHERE `username`=%s", (username))
            con.commit()
    
    return (True, "Аккаунт удалён")


@handle_pymysql_errors
def unbanSkinByUsername(username: str) -> tuple[bool, str]:
    account = getAccountByUsername(username)
    if account is None:
        return ErrorUsernameNotFound

    elif not account.skinBanned:
        return (False, "Аккаунту уже можно менять скин")

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET `skinBanned`=0, `skinBannedReason`='' WHERE `username`=%s", (username, ))
            con.commit()
    
    return (True, "Возможность аккаунта менять скин теперь разблокирована")


@handle_pymysql_errors
def getBanStateByUsername(username: str) -> tuple[bool, bool|str]:
    account = getAccountByUsername(username)
    if account is None:
        return ErrorUsernameNotFound
    
    return (True, bool(account.skinBanned))
