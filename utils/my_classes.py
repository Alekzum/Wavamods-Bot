from dataclasses import dataclass


@dataclass
class Account:
    uid: int
    """Account owner's ID"""
    login: str
    password: str
    skin: str