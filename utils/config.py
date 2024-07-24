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
RCON_HOST = get_field("RCON_HOST", "Need RCON host: ")
RCON_PORT: int = int(get_field("RCON_PORT", "Need RCON port: "))
RCON_PASSWORD = get_field("RCON_PASSWORD", "Need password for RCON: ")
STUPIDWALLET_TOKEN = get_field("STUPIDWALLET_TOKEN", "Need API-KEY from https://stupidwallet_bot.t.me: ")
SUPPORT_NAME = get_field("SUPPORT_NAME", "Your username (for command /privacy): ")
