from dataclasses import dataclass


@dataclass
class Account:
    username: str
    password: str
    skinURL: str