import json
import sqlite3

from django.core.management import BaseCommand
from django.conf import settings
from django.contrib.auth.models import User

from asgiref.sync import sync_to_async

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram import Bot, Dispatcher, executor, types
from channels.db import database_sync_to_async

from ...helpers.log_catcher import log_catcher

class FSMRegister(StatesGroup):
    user_json = State()


@log_catcher
async def command_auth(message: types.Message, state, raw_state, command):
    b_cancel = ReplyKeyboardMarkup()
    b_cancel.row(KeyboardButton('Cancel'))
    await FSMRegister.user_json.set()
    await message.reply("Welcome! Enter your json with "
                        "users like in this example: "
                        "{'login': 'user_id'} ",
                        reply_markup=b_cancel)


async def register_users(message: types.Message, state: FSMContext):
    response = message.text
    try:
        json_acceptable_string = response.replace("'", "\"")
        dict_response = json.loads(json_acceptable_string)
        for key in dict_response:
            user_id = dict_response[key]
            if user_id:
                await sync_to_async(User.objects.create_user)\
                    (username=key, password=str(user_id))
            else:
                await message.reply(f"'{key}' has not user_id")
        await state.finish()
        success_message = f"Done! Site url:" \
                          f"{settings.ALLOWED_HOSTS[0] + '/login'}"
        await message.reply(success_message,
                            reply_markup=ReplyKeyboardRemove())
    except sqlite3.IntegrityError:
        await message.reply('User already exists')
    except Exception as e:
        print(e)
        await state.finish()
        await message.reply('Something went wrong! Check your message',
                            reply_markup=ReplyKeyboardRemove())


async def cancel_register_users(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('Cancelling registration',
                         reply_markup=ReplyKeyboardRemove())


class Command(BaseCommand):
    help = 'Telegram bot'

    def handle(self, *args, **options):
        bot = Bot(token=settings.TG_TOKEN)
        storage = MemoryStorage()
        dp = Dispatcher(bot, storage=storage)

        dp.register_message_handler(command_auth,
                                    commands=['start', 'register'])
        dp.register_message_handler(cancel_register_users,
                                    Text(equals='Cancel'),
                                    state='*')
        dp.register_message_handler(register_users, state=FSMRegister.user_json)

        executor.start_polling(dp, skip_updates=True)
