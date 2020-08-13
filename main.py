# todo update_datetime_last_visit_user, emojize, interface, logging, asyncio
import logging

from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message, ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

try:
    from settings import TELEGRAM_TOKEN, CITY, MAX_COUNT_FAVOURITE_CITY
except ImportError:
    exit('copy settings.py.default settings.py and set TOKEN')

from models import db, Users, Towns, UsersFavouriteTowns, QueryHistory
from weather_forecaster import WeatherForecaster


logging.basicConfig(level=logging.INFO)

bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher(bot)

wf = WeatherForecaster()

db.connect()
db.create_tables([Users, Towns, UsersFavouriteTowns, QueryHistory])
users = Users()
towns = Towns()
uft = UsersFavouriteTowns()
history = QueryHistory()


@dp.message_handler(commands=['start', 'help'])
async def example_bot_operation(message: Message):
    users.insert_or_update_users_data(user_id=message.from_user.id)
    helper_text = f'Напишите город, чтобы узнать погоду, например:\n{CITY}'
    forecast, city = wf.get_forecast(city=CITY)
    await message.answer(f'{helper_text}\n{forecast}\n')


@dp.message_handler(commands=['rm'])
async def delete_all_favourite_cities_users(message: Message):
    user_id = message.from_user.id
    users.update_datetime_last_visit_user(user_id=user_id)

    uft.delete_all_favourite_towns_from_user(user_id=user_id)
    await message.answer(text='Удаляю все любимые города',
                         reply_markup=ReplyKeyboardRemove())


@dp.message_handler(content_types=['text'])
async def get_weather_forecast(message: Message):
    user_id = message.from_user.id
    users.update_datetime_last_visit_user(user_id=user_id)

    forecast, city = wf.get_forecast(city=message.text.strip().lower())
    if city:
        towns.insert_or_update_towns_data(town_name=city,
                                          country=wf.response['sys']['country'])
        history.insert_query(towns_table=towns, user_id=user_id, town_name=city)
        keyboard = await create_keyboard_favourite_city()
        await bot.send_message(chat_id=message.chat.id,
                               text=forecast,
                               reply_markup=keyboard)
    else:
        await bot.send_message(chat_id=message.chat.id,
                               text=forecast)


async def create_keyboard_favourite_city() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    callback_button = InlineKeyboardButton(text='Добавить как любимый город',
                                           callback_data='add_favourite_city')
    keyboard.add(callback_button)
    return keyboard


@dp.callback_query_handler(lambda i: i.data == 'add_favourite_city')
async def add_favourite_city(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query_id=callback_query.id)
    user_id = callback_query.from_user.id
    users.update_datetime_last_visit_user(user_id=user_id)

    chat_id = callback_query.message.chat.id
    # todo get city normal
    city = callback_query.message.text.split('\n', 1)[0].split(' ')[1]
    town_id = towns.get_town_id(town_name=city)
    result = uft.checking_favourite_town_name(user_id=user_id, town_id=town_id)
    cases = {
        True: message_of_add_favourite_city,
        False: message_of_exists_favourite_city,
        None: message_of_quantity_limitation_favourite_cities
    }
    await cases[result](**{
        'user_id': user_id,
        'chat_id': chat_id,
        'city': city,
    })


async def message_of_quantity_limitation_favourite_cities(**kwargs):
    await bot.send_message(chat_id=kwargs['chat_id'],
                           text=f'Не могу добавить больше '
                           f'{MAX_COUNT_FAVOURITE_CITY} любимых городов')


async def message_of_exists_favourite_city(**kwargs):
    await bot.send_message(chat_id=kwargs['chat_id'],
                           text=f"{kwargs['city']} уже есть в любимых городах")


async def message_of_add_favourite_city(**kwargs):
    keyboard_cities = await get_keyboard_cities(user_id=kwargs['user_id'])
    await bot.send_message(chat_id=kwargs['chat_id'],
                           text=f"{kwargs['city']} добавлен в любимые города",
                           reply_markup=keyboard_cities)


async def get_keyboard_cities(user_id: int) -> ReplyKeyboardMarkup:
    all_favourite_towns = towns.get_all_favourite_towns(user_id=user_id)
    buttons = [KeyboardButton(city) for city in all_favourite_towns]
    keyboard_cities = ReplyKeyboardMarkup(resize_keyboard=True)
    if len(buttons) % 2:
        for i, button in enumerate(buttons):
            if i == 0:
                keyboard_cities.row(button)
            elif not i % 2:
                keyboard_cities.row(buttons[i - 1], button)
    else:
        for i, button in enumerate(buttons):
            if i % 2:
                keyboard_cities.row(buttons[i - 1], button)
    return keyboard_cities


if __name__ == '__main__':
    executor.start_polling(dispatcher=dp, skip_updates=True)
    db.close()
