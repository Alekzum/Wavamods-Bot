from typing import Optional

from ..my_classes import Account as _Account

from . import my_banlist as _block
from . import my_database as _db


ErrorUsernameNotFound = _db.ErrorUsernameNotFound


def get_accounts_by_uid(uid: int) -> list[_Account] | None:
    return _db.getAccountsByUid(uid)


def get_usernames_by_uid(uid: int) -> list[str] | None:
    return [n.username for n in (_db.getAccountsByUid(uid) or [])]


def change_skin(username: str, skinURL: str) -> tuple[bool, str]:
    success, isBanned = _db.getBanStateByUsername(username)
    if not success and isinstance(isBanned, str):
        return (success, isBanned)
    elif isinstance(isBanned, bool) and not isBanned:
        return _db.changeSkin(username, skinURL)
    
    account = _db.getAccountByUsername(username)
    if account is None:
        return ErrorUsernameNotFound
    
    reason = "Заблокированная возможность менять скины. Причина: " + (account.skinBannedReason or "*не указанно*")
    return (False, reason)


def add_account(uid: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    return _db.addUser(uid, username, password, skinURL)


def account_is_exists(username: str) -> bool:
    return _db.accountIsExists(username)


def change_password(username: str, new_password: str) -> tuple[bool, str]:
    return _db.changePassword(username, new_password)


def get_account_count_by_uid(uid: int) -> int:
    return _db.getAccountCountByUid(uid)


def get_all_accounts() -> list[_Account] | None:
    return _db.getAllAccounts()


def get_account_by_username(username: str) -> _Account | None:
    return _db.getAccountByUsername(username)


# Admin things


def delete_account_by_username(username: str) -> tuple[bool, str]:
    return _db.deleteAccountByUsername(username)


def ban_skin_by_username(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    return _db.banSkinByUsername(username, reason)


def unban_skin_by_username(username: str) -> tuple[bool, str]:
    return _db.unbanSkinByUsername(username)


def ban_by_username(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    account = get_account_by_username(username)
    if account is None:
        return ErrorUsernameNotFound
    
    _block.banUser(account.telegramID, reason or "*Не указано*")
    return (True, "Человек забанен")


def unban_by_username(username: str) -> tuple[bool, str]:
    account = get_account_by_username(username)
    if account is None:
        return ErrorUsernameNotFound
    
    _block.unbanUser(account.telegramID)
    return (True, "Человек разбанен")


def is_banned(uid: int) -> bool:
    return _block.isBanned(uid)


def get_banned_reason(uid: int) -> str:
    return _block.getBannedReason(uid)