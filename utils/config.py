import pathlib
import dotenv


FSM_PATH = str(pathlib.Path("data/fsm_starage.db"))


def get_token() -> str:
    maybe_token: str | None = dotenv.get_key(".env", "TOKEN")
    if maybe_token is not None and maybe_token:
        return maybe_token
    
    temp_token = input("Need bot's token (https://botfather.t.me): ")
    dotenv.set_key(".env", "TOKEN", temp_token)
    return temp_token or get_token()


path = dotenv.find_dotenv()
if path == "":
    with open(".env", "w") as f:
        pass

TOKEN: str = get_token()
