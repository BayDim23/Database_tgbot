import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message,FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
import aiohttp
from config import TOKEN
import logging
import sqlite3



logging.basicConfig(level=logging.INFO)


bot = Bot(token=TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    name = State()
    age = State()
    grade = State()

def init_db():
    conn = sqlite3.connect('students')
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	age INTEGER NOT NULL,
	grade TEXT NOT NULL)
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
    await message.answer(f"Напиши твой класс!")
    await state.set_state(Form.grade)

@dp.message(Form.grade)
async def grade(message: Message, state: FSMContext):
    user_data = await state.get_data()
    # Сохраняем информацию о городе в состояние
    await state.update_data(grade=message.text)
    # Теперь можно получить все данные
    school_data = await state.get_data()

    conn = sqlite3.connect('students')
    cur = conn.cursor()

    cur.execute('''
    INSERT INTO users (name, age, grade) VALUES (?, ?, ?)''',(school_data['name'], school_data['age'], school_data['grade']))
    conn.commit()
    conn.close()

    await message.answer(f"Спасибо за регистрацию {user_data['name']}")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":  # Исправлено имя
    asyncio.run(main())