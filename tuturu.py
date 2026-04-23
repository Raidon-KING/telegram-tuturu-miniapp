import asyncio
import logging
import os
from dotenv import load_dotenv  # НОВОЕ

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

load_dotenv()  # НОВОЕ: читаем .env

WEBAPP_URL = "https://tuturu-3gfy.onrender.com"
API_TOKEN = os.environ["BOT_TOKEN"]  # НОВОЕ: берем из окружения

bot = Bot(token=API_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть наш камень 🔷",
                    web_app={"url": WEBAPP_URL}
                )
            ]
        ]
    )

    await message.answer(
        "Привет! Здесь будет мини-приложение, где вы выращиваете общий камень, "
        "который усиливается от вашего общения.",
        reply_markup=keyboard
    )


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())