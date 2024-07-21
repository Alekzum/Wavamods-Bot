from typing import Literal
import pathlib
import dotenv


FSM_PATH = str(pathlib.Path("data/fsm_starage.db"))
FIELDS: Literal["BOT_TOKEN", "DB_ID", "DB_USER", "DB_PASS", "DB_NAME"] 


def get_field(fieldName: str, hint="Need {fieldName}:") -> str:
    maybeThing: str | None = dotenv.get_key(".env", fieldName)
    if maybeThing is not None and maybeThing:
        return maybeThing
    
    maybeThing = input(hint.format(fieldName=fieldName))
    dotenv.set_key(".env", fieldName, maybeThing)
    return maybeThing or get_field(fieldName)


def get_token() -> str:
    maybe_token: str | None = dotenv.get_key(".env", "BOT_TOKEN")
    if maybe_token is not None and maybe_token:
        return maybe_token
    
    temp_token = input("Need bot's token (https://botfather.t.me): ")
    dotenv.set_key(".env", "BOT_TOKEN", temp_token)
    return temp_token or get_token()


path = dotenv.find_dotenv()
if path == "":
    with open(".env", "w") as f:
        pass


BOT_TOKEN: str = get_token()
DB_HOST = get_field("DB_HOST", "Need host with database (127.0.0.0 for example): ")
DB_USER = get_field("DB_USER", "Need login for database connection: ")
DB_PASS = get_field("DB_PASS", "Need password for database connection: ")
DB_NAME = get_field("DB_NAME", "Need table's name: ")
DB_SALT: str = get_field("DB_SALT", "Optional feature: salt to hashing passwords: ")
ADMIN_IDS: list[int] = [int(a) for a in get_field("ADMIN_IDS").replace(" ", "").split(",")]
