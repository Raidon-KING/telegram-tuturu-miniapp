import asyncio
import logging
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

logging.basicConfig(level=logging.INFO)

load_dotenv()

WEBAPP_URL = "https://tuturu-3gfy.onrender.com"
API_TOKEN = os.environ["BOT_TOKEN"]
print("BOT API_TOKEN prefix:", API_TOKEN[:10])

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    # Аргумент после /start, например "ref_abc123"
    args = message.get_args()  # aiogram 3.x
    start_param = args.strip() if args else ""

    # Строим URL мини-аппа. Важно: параметр tgWebAppStartParam.
    if start_param:
        webapp_url = f"{WEBAPP_URL}?tgWebAppStartParam={start_param}"
    else:
        webapp_url = WEBAPP_URL

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть наш камень 🔷",
                    web_app={"url": webapp_url}
                )
            ]
        ]
    )

    text = (
        "Привет! Здесь мини-приложение, где вы выращиваете общий камень, "
        "который усиливается от вашего общения."
    )
    if start_param:
        text += f"\n\nЯ вижу реф-код: {start_param}"

    await message.answer(text, reply_markup=keyboard)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())