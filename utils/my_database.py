from typing import TypedDict
import json
import time
import os


DB_PATH = os.sep.join(["data", "users.json"])
DB_FILENAME = str(DB_PATH)
SPLITTER = ","


class FILE_FIELDS(TypedDict):
    users: dict[int, list[str]]
    accounts: list[str]


_fileBusy = False
_update_time = 0.01


def wait_unlock():
    global _fileBusy
    while _fileBusy:
        time.sleep(_update_time)


def lock_file():
    global _fileBusy
    _fileBusy = True


def unlock_file():
    global _fileBusy
    _fileBusy = False


def WithLocking(func):
    def inner(*args, **kwargs):
        wait_unlock()
        lock_file()
        result = func(*args, **kwargs)
        unlock_file()
        return result
    return inner


@WithLocking
def load_raw() -> FILE_FIELDS:
    try:
        with open(DB_FILENAME, encoding="utf-8") as file:
            raw = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        raw = dict(users=dict(), accounts=list())
    return raw


@WithLocking
def save_raw(raw):
    with open(DB_FILENAME, "w", encoding="utf-8") as file:
        json.dump(raw, file, ensure_ascii=False, separators=(',', ':'))


def addAccount(uid: int, account: str) -> tuple[bool, str]:
    isExists = accountIsExists(account)
    if isExists: return (False, "Этот аккаунт уже в белом списке")

    raw = load_raw()
    if uid not in raw['users']:
        raw['users'][uid] = []
    raw['users'][uid].append(account)
    
    raw['accounts'].append(account)
    save_raw(raw)
    return True, ""


def removeAccount(uid: int, account: str) -> tuple[bool, str]:
    isExists = accountIsExists(account)
    if not isExists: return (False, "Этот аккаунт не в белом списке")

    raw = load_raw()
    if uid in raw['users'] and account in raw['users'][uid]:
        raw['users'][uid].remove(account)  
    if account in raw['accounts']:
        raw['accounts'].remove(account)
    save_raw(raw)
    return True, ""


def accountIsExists(account: str) -> bool:
    raw = load_raw()
    return account in raw['accounts']