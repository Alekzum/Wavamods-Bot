from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    """
    username (str) - Account's username

    password (str) - Account's password
    
    telegramID (int) -  Account owner's ID in Telegram
    """
    username: str
    password: str
    telegramID: int

    def __str__(self) -> str:
        return (f"Аккаунт с ником {self.username}")
    
    def __repr__(self) -> str:
        username, password, telegramID = self.username, self.password, self.telegramID,
        return f"""Account({username=}, {password=}, {telegramID=})"""
