from typing import Optional, Literal

from ..my_classes import Account

from . import my_banlist as _block
from . import my_database as _db


# Warning! Author use mypy, so there is very much "assert"s D:
ErrorUsernameNotFound = _db.ErrorUsernameNotFound


def get_accounts_by_uid(uid: int) -> tuple[Literal[True], list[Account] | None] | tuple[Literal[False], str]:
    return _db.getAccountsByUid(uid)


def get_usernames_by_uid(uid: int) -> tuple[Literal[True], list[str] | None] | tuple[Literal[False], str]:
    success, accounts = (_db.getAccountsByUid(uid) or [])
    if not success:
        assert isinstance(accounts, str), "wth"
        return (False, accounts)
    assert isinstance(accounts, list), "wth"
    accounts = accounts or []
    return (True, [n.username for n in accounts])


def change_skin(username: str, skinURL: str) -> tuple[bool, str]:
    success, isBanned = _db.getBanStateByUsername(username)
    if not success:
        assert isinstance(isBanned, str), "wth"
        return (False, isBanned)
    elif isinstance(isBanned, bool) and not isBanned:
        return _db.changeSkin(username, skinURL)
    
    success, account = get_account_by_username(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    elif account is None:
        return ErrorUsernameNotFound
    
    assert isinstance(account, Account), "wth"
    reason = "Заблокированная возможность менять скины. Причина: " + (account.skinBannedReason or "*не указанно*")
    return (False, reason)


def add_account(uid: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    return _db.addUser(uid, username, password, skinURL)


def account_is_exists(username: str) -> tuple[Literal[True], bool] | tuple[Literal[False], str]:
    return _db.accountIsExists(username)


def change_password(username: str, new_password: str) -> tuple[bool, str]:
    return _db.changePassword(username, new_password)


def get_account_count_by_uid(uid: int) -> tuple[Literal[True], int] | tuple[Literal[False], str]:
    return _db.getAccountCountByUid(uid)


def get_all_accounts() -> tuple[Literal[True], list[Account] | list] | tuple[Literal[False], str]:
    return _db.getAllAccounts()


def get_account_by_username(username: str) -> tuple[Literal[True], Account | None] | tuple[Literal[False], str]:
    return _db.getAccountByUsername(username)


# Admin things


def real_delete_account_by_username(username: str) -> tuple[bool, str]:
    return _db.realDeleteAccountByUsername(username)


def delete_account_by_username(username: str) -> tuple[bool, str]:
    return _db.deleteAccountByUsername(username)


def ban_skin_by_username(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    return _db.banSkinByUsername(username, reason)


def unban_skin_by_username(username: str) -> tuple[bool, str]:
    return _db.unbanSkinByUsername(username)


def ban_by_username(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    success, account = get_account_by_username(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    elif account is None:
        return ErrorUsernameNotFound
    
    assert isinstance(account, Account), "wth"
    _block.banUser(account.telegramID, reason or "*Не указано*")
    return (True, "Человек забанен")


def unban_by_username(username: str) -> tuple[bool, str]:
    success, account = get_account_by_username(username)
    if not success:
        assert isinstance(account, str), "wth"
        return (False, account)
    elif account is None:
        return ErrorUsernameNotFound
    
    assert isinstance(account, Account), "wth"
    _block.unbanUser(account.telegramID)
    return (True, "Человек разбанен")


def is_banned(uid: int) -> bool:
    return _block.isBanned(uid)


def get_banned_reason(uid: int) -> str:
    return _block.getBannedReason(uid)


def change_owner(username: str, new_id: int) -> tuple[bool, str]:
    return _db.changeOwner(username, new_id)