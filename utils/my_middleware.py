from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message
import time


class CooldownMiddleware(BaseMiddleware):
    """If from previous update from user didn't pass *cooldown* seconds, then update will not invoked"""
    def __init__(self, cooldown: float = 0.5):
        self.cooldown = cooldown
        self.times: dict[int, float] = dict()
    
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,  # type: ignore[override]
        data: Dict[str, Any]
    ) -> Any:
        if event.from_user is not None:
            uid = event.from_user.id  # type: ignore[union-attr]
            
        elif event.sender_chat is not None:
            uid = event.sender_chat.id
        
        else:
            return await handler(event, data)

        cur_time = time.time()
        delta_time = cur_time - self.times.get(uid, 0)

        if delta_time < self.cooldown:
            return
        
        else:
            self.times[uid] = cur_time
            return await handler(event, data)
