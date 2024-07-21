from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    """
    username (str) - Account's username

    password (str) - Account's password
    
    skinURL (str) - Account's skin
    
    telegramID (int) -  Account owner's ID in Telegram
    
    skinBanned (bool) - Account can change skin in Telegram bot or not
    
    skinBannedReason (str, optional) - The reason why the account cannot change skins
    """
    username: str
    password: str
    skinURL: str
    telegramID: int
    skinBanned: Optional[bool] = None
    skinBannedReason: Optional[str] = None

    def __str__(self) -> str:
        return (f"Аккаунт с ником {self.username}. Скин аккаунта: {self.skinURL!r}. {'Не может ' if self.skinBanned else 'Может '}менять скин. "
                f"{('Причина запрета: ' + (self.skinBannedReason or '*не указано')) if self.skinBanned else ''}")
    
    def __repr__(self) -> str:
        username, password, skinURL, telegramID, skinBanned, skinBannedReason = self.username, self.password, self.skinURL, self.telegramID, self.skinBanned, self.skinBannedReason,
        return f"""Account({username=}, {password=}, {skinURL=}, {telegramID=}, {skinBanned=}, {skinBannedReason=})"""
