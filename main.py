import asyncio
import logging

from aiogram import Bot, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import Dispatcher
from aiogram.utils import exceptions, executor
from aiogram.utils.markdown import text

import config
from medicines import Medicines

loop = asyncio.get_event_loop()
bot = Bot(token=config.API_TOKEN, loop=loop)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
medicines = Medicines()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)


@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    """
    Conversation's entry point
    """
    logging.info('Старт работы бота у пользователя ' +
                 str(message.from_user.id))

    line1 = 'Привет, этот бот ищет присылаемые ему названия лекарств ' +\
            'в списке "Расстрельный список препаратов" сайта encyclopatia.ru.'

    instructions = text(line1)

    await bot.send_message(message.chat.id,
                           instructions)


@dp.message_handler()
async def process_text(message: types.Message):
    medicine = message.text.strip()

    logging.info('Пользователь ' + str(message.from_user.id) +
                 ' cпросил ' + medicine + '.')

    descriptions = medicines.get_descriptions(medicine)

    for descr in descriptions:
        await bot.send_message(message.chat.id, descr)


async def startup(dispatcher: Dispatcher):
    logging.info('Старт бота.')
    await medicines.load_medicine_list()

async def shutdown(dispatcher: Dispatcher):
    logging.info('Убиваем бота.')

    await dispatcher.storage.close()
    await dispatcher.storage.wait_closed()


def main():
    executor.start_polling(dp,
                           loop=loop,
                           skip_updates=True,
                           on_startup=startup,
                           on_shutdown=shutdown)

if __name__ == '__main__':
    main()
