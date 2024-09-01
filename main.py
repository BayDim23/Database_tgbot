import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message,FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
from config import TOKEN, open_weather_token
import logging
import sqlite3



logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    age = State()
    city = State()

def init_db():
    conn = sqlite3.connect('user_data')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	city TEXT NOT NULL)
    ''')
    conn.commit()
    conn.close()

init_db()

@dp.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await message.answer(f"Привет, как тебя зовут ?")
    await state.set_state(Form.name.state)

@dp.message(Form.name)
async def name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer(f"Сколько тебе лет?")
    await state.set_state(Form.age)

@dp.message(Form.age)
async def age(message: Message, state: FSMContext):
    await state.update_data(age=message.text)
    await message.answer(f"В каком городе живёшь?")
    await state.set_state(Form.city)

@dp.message(Form.city)
async def city(message: Message, state: FSMContext):
    user_data = await state.get_data()

    # Сохраняем информацию о городе в состояние
    await state.update_data(city=message.text)

    # Теперь можно получить все данные
    user_data = await state.get_data()

    conn = sqlite3.connect('user_data')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO users (name, age, city) VALUES (?, ?, ?)''',(user_data['name'], user_data['age'], user_data['city']))
    conn.commit()
    conn.close()

    async with aiohttp.ClientSession() as session:
        async with session.get(f"https://api.openweathermap.org/data/2.5/weather?q={user_data['city']}&appid={open_weather_token}&units=metric") as response:

            if response.status == 200:
                wether_data = await response.json()
                main = wether_data['main']
                wether = wether_data['weather'][0]

                temperature = main['temp']
                humidity = main['humidity']
                description = wether['description']

                weather_report = (f"Город - {user_data['city']}\n"
                                  f"Температура - {temperature}\n"
                                  f"Влажность - {humidity}\n"
                                  f"Описание - {description}")
                await message.answer(weather_report)
            else:
                await message.answer("Что-то пошло не так. Попробуй еще раз.")
    await state.clear()

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  # Исправлено имя
    asyncio.run(main())