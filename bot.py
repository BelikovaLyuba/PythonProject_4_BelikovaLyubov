from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, ErrorEvent, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import asyncio
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


from api import check_city, weather

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# В этой переменной будет храниться токен.
API_TOKEN = '7589216160:AAHi5biBu5SUcRGuo3rGzFn9p7HnzT4-6M8'


# Создаём бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher()


# Определение состояний
class CityForm(StatesGroup):
    city1 = State()
    city2 = State()
    city3 = State()
    weather = State()


def weather_cities(cities):
    return []


### --- ОБРАБОТЧИК КОМАНД ---
@dp.message(F.text == '/start')
async def start_command(message: types.Message):
    # Создаём кнопки
    button_help = KeyboardButton(text='/help')
    button_weather = KeyboardButton(text='/weather')

    # Создаём клавиатуру и добавляем кнопки
    reply_keyboard = ReplyKeyboardMarkup(
        keyboard=[[button_help], [button_weather]],
        resize_keyboard=True
    )
    await message.answer(
        'Привет!\n'
        'Этот бот предназначен для определения погоды на маршруте!',
        reply_markup=reply_keyboard
    )


@dp.message(F.text == '/help')
async def help_command(message: types.Message):
    await message.answer(
        'Список доступных команд:\n'
        '/start - Начать работу с ботом\n'
        '/help - Получить помощь\n'
        '/weather - Информация о погоде\n'
        'Также вы можете воспользоваться кнопками ниже.'
    )


@dp.message(F.text == '/weather')
async def weather_command(message: types.Message, state: FSMContext):
    await message.answer("Введите город отправления:")
    await state.set_state(CityForm.city1)


@dp.message(CityForm.city1)
async def handle_city1_input(message: types.Message, state: FSMContext):
    await state.update_data(city1=message.text)
    await message.answer("Введите город прибытия:")
    await state.set_state(CityForm.city3)


@dp.message(CityForm.city3)
async def handle_city3_input(message: types.Message, state: FSMContext):
    await state.update_data(city3=message.text)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Да", callback_data="city2_yes")
    keyboard_builder.button(text="Нет", callback_data="city2_no")
    keyboard = keyboard_builder.as_markup()

    await message.answer(
        'Добавить промежуточный город?',
        reply_markup=keyboard
    )


@dp.callback_query(lambda call: call.data.startswith("city2_"))
async def intermediate_city_choice(call: CallbackQuery, state: FSMContext):
    if call.data == "city2_yes":
        await call.message.edit_text("Введите промежуточный город:")
        await state.set_state(CityForm.city2)

    elif call.data == "city2_no":
        keyboard_builder = InlineKeyboardBuilder()
        keyboard_builder.button(text="Текущая погода", callback_data="weather_now")
        keyboard_builder.button(text="Прогноз на 1 день", callback_data="weather_1day")
        keyboard_builder.button(text="Прогноз на 3 дней", callback_data="weather_3days")
        keyboard = keyboard_builder.as_markup()

        await call.message.edit_text("Выберите временной интервал прогноза погоды:",
                             reply_markup=keyboard)


@dp.message(CityForm.city2)
async def handle_city2_input(message: types.Message, state: FSMContext):
    await state.update_data(city2=message.text)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Текущая погода", callback_data="weather_now")
    keyboard_builder.button(text="Прогноз на 1 день", callback_data="weather_1day")
    keyboard_builder.button(text="Прогноз на 3 дней", callback_data="weather_3days")
    keyboard = keyboard_builder.as_markup()

    await message.answer("Выберите временной интервал прогноза погоды:",
                         reply_markup=keyboard)

def format_message(text, time):
    titles = {'weather_now': 'Погода сейчас:',
              'weather_1day': 'Прогноз погоды на один день:',
              'weather_3days': 'Прогноз погоды на три дня:'}
    message = [f'Город: {text['city']}', titles[time]]
    for i in text['data']:
        message.append(f'Дата: {i['date']}\n'
                       f'Температура: {i['temp']}\n'
                       f'Осадки: {i['precipitation']}\n'
                       f'Ветер: {i['wind']}\n'
                       f'Влажность: {i['humidity']}')
    if len(message) > 5:
        message = message[:5]
    return '\n\n'.join(message)


@dp.callback_query(F.data.startswith("weather_"))
async def handle_weather_choice(call: CallbackQuery, state: FSMContext):
    data = await state.get_data()

    text = list()
    weather1 = check_city(data.get('city1'), call.data)
    if weather1['status']:
        text.append(format_message(weather1, call.data))
        if data.get('city2', None):
            weather2 = check_city(data.get('city2'), call.data)
            if weather2['status']:
                text.append(format_message(weather2, call.data))
            else:
                await call.message.edit_text(f'Ошибка: {weather2['error']}')
        weather3 = check_city(data.get('city3'), call.data)
        if weather3['status']:
            text.append(format_message(weather3, call.data))
        else:
            await call.message.edit_text(f'Ошибка: {weather3['error']}')
    else:
        text.append(f'Ошибка: {weather1['error']}')

    text.append('Спасибо за запрос!')
    await call.message.edit_text('\n\n**********\n\n'.join(text))


@dp.errors()
async def handle_error(event: ErrorEvent):
    logging.error(f'Произошла ошибка: {event.exception}')
    if event.update.message:
        await event.update.message.answer('Извините, произошла ошибка.')



### --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    async def main():
        # Запускаем polling
        await dp.start_polling(bot)

    asyncio.run(main())