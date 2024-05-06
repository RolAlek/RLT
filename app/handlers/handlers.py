import json

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from motor.motor_asyncio import AsyncIOMotorClient

from utils import calculate_sum_all_payments


router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message) -> None:
    await message.answer('Hi')


@router.message()
async def send_aggregated(
    message: Message,
    client: AsyncIOMotorClient,
) -> None:
    await message.answer(
        await calculate_sum_all_payments(
            **json.loads(message.text),
            client=client,
        )
    )
