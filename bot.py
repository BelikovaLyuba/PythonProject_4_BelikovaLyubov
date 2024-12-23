from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
import logging
import asyncio
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder


from api import check_city

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
async def weather_handler(message: types.Message, state: FSMContext):
    await message.answer("Введите город отправления:")
    await state.set_state(CityForm.city1)


@dp.message(CityForm.city1)
async def handle_city1_input(message: types.Message, state: FSMContext):
    await state.update_data(city1=message.text)
    await message.answer("Введите город прибытия:")
    await state.set_state(CityForm.city3)


@dp.message(CityForm.city3)
async def handle_city1_input(message: types.Message, state: FSMContext):
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
        keyboard_builder.button(text="Прогноз на 5 дней", callback_data="weather_5days")
        keyboard = keyboard_builder.as_markup()

        await call.message.edit_text("Выберите временной интервал прогноза погоды:",
                             reply_markup=keyboard)


@dp.message(CityForm.city2)
async def handle_city2_input(message: types.Message, state: FSMContext):
    await state.update_data(city2=message.text)

    keyboard_builder = InlineKeyboardBuilder()
    keyboard_builder.button(text="Текущая погода", callback_data="weather_now")
    keyboard_builder.button(text="Прогноз на 1 день", callback_data="weather_1day")
    keyboard_builder.button(text="Прогноз на 5 дней", callback_data="weather_5days")
    keyboard = keyboard_builder.as_markup()

    await message.answer("Выберите временной интервал прогноза погоды:",
                         reply_markup=keyboard)


# Функция для форматирования прогноза погоды
def format_weather(data, location):
    location_name = geo_storage.get(location)['name']
    forecast = f"<b>Погода в {location_name}:</b>\n"
    for part in data if isinstance(data, list) else [data]:
        forecast += (
            f"<b>Время:</b> {part.get('time', 'Сейчас')}\n"
            f"<b>Температура:</b> {part['temperature']}°C\n"
            f"<b>Ощущается как:</b> {part['real_feels_temperature']}°C\n"
            f"<b>Ветер:</b> {part['wind_speed']} м/с\n"
            f"<b>Влажность:</b> {part['humidity']}%\n"
            f"<b>Облачность:</b> {part['cloud_cover']}%\n"
            f"<b>Описание:</b> {part['description']}\n"
            f"{part['analyze_favorability']}\n\n"
        )
    return forecast


# Обработка выбора временного интервала прогноза и редактирование сообщения
@dp.callback_query(lambda call: call.data.startswith("weather_"), CityForm.weather)
async def handle_weather_choice(call: CallbackQuery, state: FSMContext):
    print(CityForm.city2)

    '''# Проверка на ошибки для обеих точек
    if weather_data_city1['status'] == 'error':
        await call.message.edit_text(f"Ошибка: {weather_data_city1['message']}")
        return
    if weather_data_city2['status'] == 'error':
        await call.message.edit_text(f"Ошибка: {weather_data_city2['message']}")
        return

    # Форматирование прогноза для обеих точек
    forecast_city1 = format_weather(weather_data_city1['data'], city1)
    forecast_city2 = format_weather(weather_data_city2['data'], city2)

    # Редактирование сообщения с результатом выбора
    await call.message.edit_text(f"{forecast_city1}\n\n{forecast_city2}", parse_mode="HTML")
    await state.clear()  # Очищаем состояние после завершения диалога
    await call.answer()'''

'''

@dp.message(F.text == '/weather')
async def weather_command(message: types.Message):
    await message.answer(
        'Список доступных команд:\n'
        '/start - Начать работу с ботом\n'
        '/help - Получить помощь\n'
        'Также вы можете воспользоваться кнопками ниже.'
    )

### --- ОБРАБОТКА ТЕКСТОВЫХ СООБЩЕНИЙ ---
@dp.message(F.text == 'О боте')
async def about_bot(message: types.Message):
    await message.answer('Этот бот создан для демонстрации возможностей библиотеки Aiogram!')

### --- ИНЛАЙН-КНОПКИ ---
@dp.message(F.text == 'Инлайн-кнопки')
async def send_inline_keyboard(message: types.Message):
    # Создаём инлайн-кнопки
    button_link = InlineKeyboardButton(text='Ссылка', url='https://example.com')
    button_callback = InlineKeyboardButton(text='Голосовать', callback_data='vote')

    # Создаём инлайн-клавиатуру
    inline_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[[button_link], [button_callback]]
    )

    await message.answer('Выберите действие:', reply_markup=inline_keyboard)

### --- CALLBACK-ЗАПРОСЫ ---
@dp.callback_query(F.data == 'vote') 
async def vote_callback(callback: types.CallbackQuery):
    await callback.message.answer('Спасибо за ваш голос!')
    await callback.answer()

### --- НЕОБРАБОТАННЫЕ СООБЩЕНИЯ ---
@dp.message()
async def handle_unrecognized_message(message: types.Message):
    await message.answer('Извините, я не понял ваш запрос. Попробуйте использовать команды или кнопки.')'''

'''@dp.errors()
async def handle_error(event: ErrorEvent):
    logging.error(f'Произошла ошибка: {event.exception}')
    if event.update.message:
        await event.update.message.answer('Извините, произошла ошибка.')'''

### --- ЗАПУСК БОТА ---
if __name__ == '__main__':
    async def main():
        # Запускаем polling
        await dp.start_polling(bot)

    asyncio.run(main())