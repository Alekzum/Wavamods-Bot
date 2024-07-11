from typing import Optional

from ..my_checkers import check_skin, check_password
from ..my_classes import Account as _Account

from . import my_binds as _binds  # type: ignore
from . import my_database as _db  # type: ignore


def get_accounts_by_uid(uid: int) -> list[_Account] | None:
    return _db.getAccountsByUid(uid)


def get_usernames_by_uid(uid: int) -> list[str] | None:
    return [n.username for n in (_db.getAccountsByUid(uid) or [])]


def change_skin(username: str, password: str, skinURL: str) -> tuple[bool, str]:
    success, isBanned = _db.getBanStateByUsername(username)
    if not success and isinstance(isBanned, str):
        return (success, isBanned)
    elif isinstance(isBanned, bool) and not isBanned:
        return _db.changeSkin(username, password, skinURL)
    
    account = _db.getAccountByUsername(username)
    if account is None:
        return _db.ErrorUsernameNotFound
    
    reason = "Заблокированная возможность менять скины. Причина: " + (account.skinBannedReason or "*не указанно*")
    return (False, reason)


def add_account(uid: int, username: str, password: str, skinURL: Optional[str] = None) -> tuple[bool, str]:
    return _db.addUser(uid, username, password, skinURL)


def account_is_exists(username: str) -> bool:
    return _db.accountIsExists(username)


def change_password(username: str, old_password: str, new_password: str) -> tuple[bool, str]:
    return _db.changePassword(username, old_password, new_password)


def get_account_count_by_uid(uid: int) -> int:
    return _db.getAccountCountByUid(uid)


def get_all_accounts() -> list[_Account] | None:
    return _db.getAllAccounts()


def get_account_by_username(username: str) -> _Account | None:
    return _db.getAccountByUsername(username)


def ban_skin_by_username(username: str, reason: Optional[str] = None) -> tuple[bool, str]:
    return _db.banSkinByUsername(username, reason)


def unban_skin_by_username(username: str) -> tuple[bool, str]:
    return _db.unbanSkinByUsername(username)


def get_ban_state_by_username(username: str) -> tuple[bool, str]:
    success, ban_state = _db.getBanStateByUsername(username)
    if not success and isinstance(ban_state, str):
        return (success, ban_state)
    
    reason = "Без указания причины" if isinstance(ban_state, bool) else ban_state
    return (success, reason)