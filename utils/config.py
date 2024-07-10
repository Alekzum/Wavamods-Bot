from typing import Literal
import pathlib
import dotenv


FSM_PATH = str(pathlib.Path("data/fsm_starage.db"))
FIELDS: Literal["BOT_TOKEN", "DB_ID", "DB_LOGIN", "DB_PASSWORD", "DB_NAME"] 


def get_field(fieldName: str) -> str:
    maybeThing: str | None = dotenv.get_key(".env", fieldName)
    if maybeThing is not None and maybeThing:
        return maybeThing
    
    maybeThing = input(f"Need {fieldName}: ")
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
DB_IP = get_field("DB_IP")
DB_LOGIN = get_field("DB_LOGIN")
DB_PASSWORD = get_field("DB_PASSWORD")
DB_NAME = get_field("DB_NAME")
