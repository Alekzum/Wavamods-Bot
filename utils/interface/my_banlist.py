from typing import TypedDict
import pathlib
import json
import time


BANS_PATH = pathlib.Path("data/banlist.json")
BANS_FILENAME = str(BANS_PATH)
SPLITTER = ","


# uid INTEGER UNIQUE,
# banned INTEGER,
# bannedReason TEXT


class FIELDS(TypedDict):
    banned: bool
    bannedReason: None | str

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
def load_raw() -> dict[int, FIELDS]:
    try:
        with open(BANS_FILENAME, encoding="utf-8") as file:
            raw = json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        raw = {}
    return raw


@WithLocking
def save_raw(raw):
    with open(BANS_FILENAME, "w", encoding="utf-8") as file:
        json.dump(raw, file, ensure_ascii=False, separators=(',', ':'))


def banUser(uid: int, reason: str):
    raw = load_raw()
    raw[uid] = dict(banned=True, bannedReason=reason)
    save_raw(raw)
#     with sqlite3.connect(BANS_FILENAME) as con:
#         cur = con.cursor()
#         cur.execute(f"INSERT INTO {TABLE_NAME} (uid, banned, bannedReason) VALUES (?, 1, ?)", (uid, reason))
#         con.commit()


def unbanUser(uid: int):
    raw = load_raw()
    raw[uid] = dict(banned=False, bannedReason=None)
    save_raw(raw)
#     with sqlite3.connect(BANS_FILENAME) as con:
#         cur = con.cursor()
#         cur.execute(f"DELETE FROM {TABLE_NAME} WHERE uid=?", (uid, ))
#         con.commit()


def getBannedUsers() -> list[int] | list:
    raw = load_raw()
    result = [k for (k, v) in raw.items() if v.get("banned")]
    return result
    
#     with sqlite3.connect(BANS_FILENAME) as con:
#         cur = con.cursor()
#         cur.execute(f"SELECT uid FROM {TABLE_NAME} WHERE banned=1", ())
#         results = cur.fetchall()
#     return results or []


# def getBannedReason(uid: int) -> str:
#     with sqlite3.connect(BANS_FILENAME) as con:
#         cur = con.cursor()
#         cur.execute(f"SELECT bannedReason FROM {TABLE_NAME} WHERE uid=?", (uid, ))
#         result = cur.fetchone()
#     return result or "*не указано*"


def isBanned(uid: int) -> bool:
    return uid in getBannedUsers()