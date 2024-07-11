from dataclasses import dataclass
from typing import Optional


@dataclass
class Account:
    username: str
    password: str
    skinURL: str
    skinBanned: bool
    telegramID: int
    skinBannedReason: Optional[str] = None

    def __str__(self) -> str:
        return (f"Аккаунт с ником {self.username}. Пароль от аккаунта: {self.password!r}. "
                f"Скин аккаунта: {self.skinURL!r}. {'Не' if self.skinBanned else ''} может менять скин. "
                f"{('Причина запрета: ' + (self.skinBannedReason or '*не указано')) if self.skinBanned else ''}")
    
    def __repr__(self) -> str:
        username, password, skinURL = self.username, self.password, self.skinURL
        return f"""utils.my_classes.Account({username=}, {password=}, {skinURL=})"""
