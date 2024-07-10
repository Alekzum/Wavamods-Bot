from typing import Optional

from ..my_classes import Account as _Account

from . import my_binds as _binds  # type: ignore
from . import my_database as _db  # type: ignore


def get_accounts_by_uid(uid: int) -> list[_Account] | list:
    user_usernames = _binds.getBinds(uid)
    user_accounts = [_db.getUserByUsername(username) for username in user_usernames]
    return user_accounts


def get_logins_by_uid(uid: int) -> list[str] | None:
    user_usernames = _binds.getBinds(uid)
    return user_usernames


def change_skin(uid: int, username: str, password: str, skinURL: str) -> tuple[bool, str]:
    return _db.changeSkin(uid, username, password, skinURL)


def add_user(uid: int, username: str, password: str, skinURL: Optional[str] = None)  -> tuple[bool, str]:
    temp_result = _db.addUser(uid, username, password, skinURL)
    if temp_result[0]:
        _binds.addBind(uid, username)
    
    return temp_result


def user_is_exists(username: str) -> bool:
    return _db.userIsExists(username)


def get_account_count_by_uid(uid: int) -> int:
    return _db.getAccountCountByUid(uid)

