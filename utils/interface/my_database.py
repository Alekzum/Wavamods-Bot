# from html.parser import escape, unescape
from ..config import DB_HOST, DB_NAME, DB_USER, DB_PASS, DB_SALT
from ..my_classes import Account
from typing import Optional, TypedDict, Literal, Any
import pymysql.cursors  # type: ignore
import pymysql  # type: ignore
import logging
import hashlib
from io import StringIO


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


def connect_to_remote_database():
    connection = pymysql.connect(
        database=DB_NAME, host=DB_HOST, user=DB_USER, password=DB_PASS, cursorclass=pymysql.cursors.DictCursor
    )
    return connection


def text_to_sha512(text: str) -> str:
    salted_text = DB_SALT + text + DB_SALT
    return hashlib.sha256(salted_text.encode("utf-8")).hexdigest()


def handle_pymysql_errors(func):
    def inner(*args, **kwargs) -> Any | tuple[Literal[False], str]:
        try:
            return func(*args, **kwargs)
        except pymysql.err.Error as ex:
            logger.error(repr(ex))
            return (False, f"Произошла ошибка {ex!r} при работе с БД")
    return inner


def accountIsExists(username: str) -> tuple[Literal[True], bool] | tuple[Literal[False], str]:
    success, accounts = getAllAccounts()
    if not success:
        return (success, accounts)

    temp_result = [a.username.lower() for a in accounts or []]
    return (True, username.lower() in temp_result)


@handle_pymysql_errors
def getAccountByUsername(username: str) -> tuple[Literal[True], Account | None] | tuple[Literal[False], str]:
    """return Account type or error if something wrong"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}` WHERE `username`=%s", (username, ))
            result: ACCOUNT_TUPLE | None = cur.fetchone()
    return (True, Account(**result) if result else None)


@handle_pymysql_errors
def addUser(telegramID: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    """return tuple like (success, message)"""
    success, already_exists = accountIsExists(username)
    if not success:
        assert isinstance(already_exists, str), "wth"
        return (False, already_exists)
    
    elif already_exists:
        return (False, "Данный ник занят")

    elif skinURL is None:
        skinURL = ""

    password = text_to_sha512(password)

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"INSERT INTO `{TABLE_NAME}` (`username`, `password`, `skinURL`, `telegramID`) VALUES (%s, %s, %s, %s)", (username, password, skinURL, telegramID, ))
            con.commit()
    
    return (True, "Пользователь добавлен в базу данных")


@handle_pymysql_errors
def getAccountCountByUid(telegramID: int) -> tuple[Literal[True], int] | tuple[Literal[False], str]:
    """Return int aka "how much user with ID have accounts?" """
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT * FROM `{TABLE_NAME}` WHERE `telegramID`=%s", (telegramID, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return (True, len(result) if result else 0)


@handle_pymysql_errors
def getAccountsByUid(telegramID: int) -> tuple[Literal[True], list[Account] | None] | tuple[Literal[False], str]:
    """return list like [Account1, Account2, Account3]"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}` WHERE `telegramID`=%s", (telegramID, ))
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return (True, [Account(**t) for t in result] if result else None)


@handle_pymysql_errors
def getAllAccounts() -> tuple[Literal[True], list[Account] | None] | tuple[Literal[False], str]:
    """return list like [Account1, Account2, Account3]"""
    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"SELECT `username`, `password`, `skinURL`, `skinBanned`, `skinBannedReason`, `telegramID` FROM `{TABLE_NAME}`", ())
            result: list[ACCOUNT_TUPLE] | None = cur.fetchall()
    return (True, [Account(**t) for t in result] if result else None)


@handle_pymysql_errors
def changeSkin(username: str, skinURL: str) -> tuple[bool, str]:
    """return tuple like (success, message)"""
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound

    elif account.skinBanned:
        return (False, "Аккаунту запрещено менять скин. Причина: " + (account.skinBannedReason or "*Не указано*"))

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET skinURL=%s WHERE `username`=%s", (skinURL, username, ))
            con.commit()
    
    return (True, "Скин пользователя обновлён")


@handle_pymysql_errors
def changePassword(username: str, password: str) -> tuple[bool, str]:
    """return tuple like (success, message)"""
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound
    
    password = text_to_sha512(password)

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET password=%s WHERE `username`=%s", (password, username, ))
            con.commit()
    
    return (True, "Пароль пользователя обновлён")


@handle_pymysql_errors
def banSkinByUsername(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
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
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET `telegramID`=1415937101, `skinURL`='' WHERE `username`=%s", (username))
            con.commit()
    
    return (True, "Аккаунт удалён")


@handle_pymysql_errors
def unbanSkinByUsername(username: str) -> tuple[bool, str]:
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
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
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound
    
    return (True, bool(account.skinBanned))


@handle_pymysql_errors
def realDeleteAccountByUsername(username: str) -> tuple[bool, str]:
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"DELETE FROM `{TABLE_NAME}` WHERE `username`=%s", (username))
            con.commit()
    
    return (True, "Аккаунт удалён")


@handle_pymysql_errors
def changeOwner(username: str, new_id: int) -> tuple[bool, str]:
    success, account = getAccountByUsername(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    
    elif account is None:
        return ErrorUsernameNotFound

    with connect_to_remote_database() as con:
        with con.cursor() as cur:
            cur.execute(f"UPDATE `{TABLE_NAME}` SET `telegramID`=%s WHERE `username`=%s", (new_id, username))
            con.commit()
    
    return (True, "Аккаунт удалён")
