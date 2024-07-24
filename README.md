# Wavamods-Bot

## Description
Just append username to whitelist in server via MCRCON after spending some amount of [StupidWallet's coins](https://t.me/stupidwallet_bot)

## Installation
Download this project and just run `main.py` with python 3.12+. 

Packages will be downloaded automatically. 

You need bot's token, RCON's host, port and password, [StupidWallet's API token](https://t.me/stupidwallet_bot). You can write it interactively through console, or use `.env.example` with renaming it to `.env`.

Also need your's username, because Telegram require command `/privacy` for all bots...

## Installation example
```
git clone this_cool_repo
cd this_cool_repo
python main.py

Collecting cryptography==43.0.0 (from -r requirements.txt (line 1))
  Using cached cryptography-43.0.0-cp39-abi3-win_amd64.whl.metadata (5.4 kB)
Collecting aiogram_sqlite_storage (from -r requirements.txt (line 2))

# and etc.

Installing collected packages: mcrcon, typing-extensions, sniffio...


Need bot's token (https://botfather.t.me): null
Need RCON host: 127.0.0.1
Need RCON port: 25565
Need password for RCON: user
Need API-KEY from https://stupidwallet_bot.t.me: 0123456789abcdef0123456789abcdef0123456789abcdef012345677889abcdef
Your username (for command /privacy): SomeCoolUser
Starting bot...
Run polling @SomeCoolBot id=13371031 - Cool bot
# when press Ctrl+C
Polling stopped @SomeCoolBot id=13371031 - Cool bot
Bot is stopped.
```

## Commands
- `/start`
- `/privacy` (oops, only on russian)
- `/add_user` (use with username, like `/add_user SomeCoolUsername`)