import pathlib
import sqlite3


BINDS_PATH = pathlib.Path("data/bocklist.db")
BINDS_FILENAME = str(BINDS_PATH)
TABLE_NAME = "Users"
SPLITTER = ","


with sqlite3.connect(BINDS_FILENAME) as con:
    cur = con.cursor()
    cur.execute(f"""CREATE TABLE IF NOT EXISTS {TABLE_NAME}(
    uid INTEGER UNIQUE,
    banned INTEGER,
    bannedReason TEXT
)""")


def banUser(uid: int, reason: str):
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute(f"INSERT INTO {TABLE_NAME} (uid, banned, bannedReason) VALUES (?, 1, ?)", (uid, reason))
        con.commit()


def unbanUser(uid: int):
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM {TABLE_NAME} WHERE uid=?", (uid, ))
        con.commit()


def getBannedUsers() -> list[int] | list:
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute(f"SELECT uid FROM {TABLE_NAME} WHERE banned=1", ())
        results = cur.fetchall()
    return results or []


def getBannedReason(uid: int) -> str:
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute(f"SELECT bannedReason FROM {TABLE_NAME} WHERE uid=?", (uid, ))
        result = cur.fetchone()
    return result or "*не указано*"


def isBanned(uid: int) -> bool:
    return uid in getBannedUsers()