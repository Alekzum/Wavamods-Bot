import pathlib
import sqlite3


BINDS_PATH = pathlib.Path("data/binds.db")
BINDS_FILENAME = str(BINDS_PATH)

content: dict[int, list[str]]


with sqlite3.connect(BINDS_FILENAME) as con:
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS Binds(
    uid INTEGER,
    username STRING
)""")


def addBind(uid: int, username: str):
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute("INSERT INTO Binds (uid, username) VALUES (?, ?)", (uid, username))
        con.commit()


def getBinds(uid: int) -> list[str] | list:    
    with sqlite3.connect(BINDS_FILENAME) as con:
        cur = con.cursor()
        cur.execute("SELECT username FROM Binds WHERE uid=?", (uid, ))
        results: list[tuple[str]] | list = cur.fetchall()

    result = [r and r[0] for r in results] 
    return result
