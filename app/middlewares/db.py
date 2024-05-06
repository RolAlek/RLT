from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from motor.motor_asyncio import AsyncIOMotorClient


class DbSessionMiddleware(BaseMiddleware):
    def __init__(self, session_pool: AsyncIOMotorClient) -> None:
        super().__init__()
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Awaitable:
        data['client'] = self.session_pool
        return await handler(event, data)
