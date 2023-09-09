import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.utils.markdown import text

import config
from medicines import Medicines

loop = asyncio.get_event_loop()
bot = Bot(token=config.BOT_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()
medicines = Medicines()

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    logging.info(f"Старт работы бота у пользователя {get_some_name(message)}")

    line1 = (
        "Привет, этот бот ищет присылаемые ему названия лекарств "
        'в списке "Расстрельный список препаратов" сайта encyclopatia.ru.'
    )

    instructions = text(line1)

    await bot.send_message(message.chat.id, instructions)


@dp.message()
async def process_text(message: types.Message):
    if not message.text:
        return

    medicine = message.text.strip()
    logging.info(f"Пользователь {get_some_name(message)} cпросил {medicine}.")
    descriptions = medicines.get_descriptions(medicine)

    for descr in descriptions:
        await bot.send_message(message.chat.id, descr)


@dp.startup()
async def startup(dispatcher: Dispatcher):
    logging.info("Старт бота.")
    await medicines.load_medicine_list()


def get_some_name(message: types.Message) -> str:
    if message.from_user:
        return f"{message.from_user.id} ({message.from_user.username})"
    else:
        return f"{message.chat.id} ({message.chat.title})"


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
