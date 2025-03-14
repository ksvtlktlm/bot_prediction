import asyncio
import logging
import random
import os
from collections import defaultdict
from datetime import datetime, date

from dotenv import load_dotenv
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup


# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Загрузка переменных окружения
load_dotenv()
TOKEN = os.getenv("TOKEN")

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()

# Словари для хранения данных пользователей
user_history = defaultdict(list) # Предсказания
user_magic_check = defaultdict(lambda: (date.min, 0)) # Магическая энергия
user_luck_check = defaultdict(lambda: (date.min, 0))  # Индекс удачи
user_ritual_check = defaultdict(lambda: (date.min, "")) # Дневные ритуалы

HISTORY_LIMIT = 3

ADMIN_ID = os.getenv("ADMIN_ID")

async def log_to_admin(bot, user_id, username, action):
    """Отправляет лог администратору."""
    log_text = f"📝 Лог: {username} (ID: {user_id}) использовал {action}"
    await bot.send_message(ADMIN_ID, log_text)

def load_predictions(filename="predictions.txt"):
    """Загружает предсказания из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            predictions = [line.strip() for line in file.readlines()]
        return predictions
    except FileNotFoundError:
        return ["Файл с предсказаниями не найден!"]

def load_oracle_questions(filename="oracle_questions.txt"):
    """Загружает вопросы от Оракула из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return ["Файл с вопросами не найден!"]

def load_daily_rituals(filename="daily_rituals.txt"):
    """Загружает дневные ритуалы из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return ["Файл с заданиями не найден!"]

def load_oracle_responses(filename="oracle_responses.txt"):
    """Загружает обобщённые ответы Оракула из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return ["Ответ ещё не найден. Попробуй спросить позже."]

def load_magic_ball_responses(filename="magic_ball_responses.txt"):
    """Загружает стандартные ответы Шара предсказаний из файла."""
    try:
        with open(filename, "r", encoding="utf-8") as file:
            return [line.strip() for line in file.readlines()]
    except FileNotFoundError:
        return ["Шар пока не настроен. Попробуй позже!"]


# Загрузка данных
oracle_questions = load_oracle_questions()
predictions = load_predictions()
daily_rituals = load_daily_rituals()
oracle_responses = load_oracle_responses()
magic_ball_responses = load_magic_ball_responses()


# Машины состояний
class OracleState(StatesGroup):
    waiting_for_answer = State()

class MagicBallState(StatesGroup):
    waiting_for_question = State()


@dp.message(Command("start"))
async def send_welcome(message: Message):
    user_name = message.from_user.first_name
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/start")
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🔮 Получить предсказание")],
            [KeyboardButton(text="✨ Узнать уровень магической энергии")],
            [KeyboardButton(text="🎲 Проверить удачу")],
            [KeyboardButton(text="🧙‍♂️ Вопрос от Оракула")],
            [KeyboardButton(text="📜 Ежедневный ритуал")],
            [KeyboardButton(text="🎱 Шар предсказаний")],
            [KeyboardButton(text="🔄 История предсказаний"), KeyboardButton(text="ℹ️ Помощь")]
        ],
        resize_keyboard=True
    )
    welcome_text = f"🔮 Привет, {user_name}!\n\nЯ – бот предсказаний. Хочешь узнать, что ждет тебя сегодня? Просто используй одну из команд ниже! 👇"
    await message.answer(welcome_text, parse_mode="Markdown", reply_markup=keyboard)

@dp.message(Command("prediction"))
async def send_prediction(message: Message):
    """Отправляет предсказание и логирует пользователя."""
    prediction = random.choice(predictions)  # Случайное предсказание
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/prediction")
    user_history[user_id].append(prediction)
    if len(user_history[user_id]) > HISTORY_LIMIT:
        user_history[user_id].pop(0)
    await message.answer("🔮 Я смотрю в будущее... Дай мне секунду... 🤔")
    await asyncio.sleep(2)
    await message.answer(f"🔮 Вот, что звезды предсказывают тебе сегодня, {user_name}:\n\n{prediction}")

@dp.message(Command("magic"))
async def magic_command(message: Message):
    """Отправляет уровень магической энергии и логирует пользователя."""
    now = datetime.now().date()
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/magic")
    if user_id in user_magic_check:
        last_check_date, magic_value = user_magic_check[user_id]
        if last_check_date == now:
            await message.answer(f"🔒 Ты уже проверял(а) свою магическую энергию сегодня!\n\n✨ Твой уровень магии: {magic_value}%\n🔄 Возвращайся завтра!")
            return
    magic_level = random.randint(10, 100)
    user_magic_check[user_id] = (now, magic_level)
    await message.answer(f"✨ Сегодня твой уровень магической энергии – {magic_level}%!")

@dp.message(Command("luck"))
async def luck_index(message: Message):
    """Отправляет уровень удачи и логирует пользователя."""
    user_id = message.from_user.id
    now = datetime.now().date()
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/luck")
    if user_id in user_luck_check:
        last_check_date, luck_value = user_luck_check[user_id]
        if last_check_date == now:
            await message.answer(f"🌟 Ты уже проверял(а) свою удачу сегодня!\n\n🎲 Твой индекс удачи: {luck_value}%\n🔄 Возвращайся завтра!")
            return
    luck_value = random.randint(1, 100)
    user_luck_check[user_id] = (now, luck_value)
    if luck_value >= 80:
        comment = "🔥 Сегодня твой день! Используй эту удачу!"
    elif luck_value >= 50:
        comment = "🙂 Вполне неплохо! Можно рискнуть!"
    else:
        comment = "🌧 Осторожнее! Сегодня не лучший день для авантюр."
    await message.answer(f"🌟 Индекс удачи на сегодня: {luck_value}%\n\n{comment}")

@dp.message(Command("oracle"))
async def oracle_question(message: Message, state: FSMContext):
    """Оракул задаёт вопрос, ждет ответа и логирует пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/oracle")
    intro_text = (
        "🧙‍♂️ *Оракул мудр и загадочен...*\n\n"
        "Оракул задаст тебе философский вопрос. После этого ты можешь написать свой ответ, "
        "а он даст тебе загадочное, но мудрое толкование. Иногда истина скрывается там, "
        "где мы её не ищем... 🔮\n\n"
        "Готов(а)? Тогда слушай внимательно... 👂"
    )
    await message.answer(intro_text, parse_mode="Markdown")
    await asyncio.sleep(2)
    question = random.choice(oracle_questions)
    await state.update_data(question=question) # Сохраняем вопрос в контексте состояния
    await message.answer(f"🔮 Оракул задаёт тебе вопрос:\n\n{question}\n\n💭 Напиши свой ответ!")
    await state.set_state(OracleState.waiting_for_answer)  # Переводим в состояние ожидания ответа

@dp.message(OracleState.waiting_for_answer)
async def oracle_response(message: Message, state: FSMContext):
    user_data = await state.get_data()  # Получаем сохранённый вопрос
    question = user_data.get("question", "Вопрос потерялся...")
    response = random.choice(oracle_responses)
    await message.answer(f"📜 Оракул говорит: {response}")
    await state.clear()

@dp.message(Command("ritual"))
async def daily_ritual(message: Message):
    """Отправляет ежедневное задание и логирует пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/ritual")
    now = datetime.now().date()
    if user_id in user_ritual_check:
        last_check_date, ritual = user_ritual_check[user_id]
        if last_check_date == now:
            await message.answer(f"📜 Твоё задание на сегодня:\n\n{ritual}\n\n🔄 Возвращайся завтра за новым!")
            return
    ritual = random.choice(daily_rituals)
    user_ritual_check[user_id] = (now, ritual)
    await message.answer(f"📜 Твоё задание дня:\n\n{ritual}")

@dp.message(Command("magicball"))
async def start_magic_ball(message: Message, state: FSMContext):
    """Шар предсказаний; ждет ответ и логирует пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/magicball")
    await message.answer("🎱 Шар предсказаний ждёт вопрос! Задай любой вопрос, и я дам ответ!", parse_mode="Markdown")
    await state.set_state(MagicBallState.waiting_for_question)

@dp.message(MagicBallState.waiting_for_question)
async def magic_ball_response(message: Message, state: FSMContext):
    response = random.choice(magic_ball_responses)
    await message.answer(f"🔮 Ответ Шара: {response}")
    await state.clear()

@dp.message(Command("history"))
async def show_history(message: Message):
    """Присылает историю в виде 3 последних предсказаний и логирует пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/history")
    if user_id not in user_history or not user_history[user_id]:
        await message.answer("📜 У тебя пока нет предсказаний. Напиши /prediction, чтобы получить первое!")
        return
    history_text = "\n\n".join(user_history[user_id])
    await message.answer(f"📜 Твоя история предсказаний:\n\n{history_text}")

@dp.message(Command("help"))
async def send_help(message: Message):
    """Присылает инструкцию по использованию бота и логирует пользователя."""
    user_id = message.from_user.id
    username = message.from_user.username or "No username"
    await log_to_admin(bot, user_id, username, "/help")
    help_text = """
ℹ️ *Как пользоваться ботом предсказаний?*

🔮 *Основные команды:*
/prediction – Получить случайное предсказание.
/magic – Узнать уровень магической энергии.
/luck – Узнать уровень удачи.
/oracle – Оракул задаст философский вопрос, а затем даст тебе мудрый ответ на твое мнение.\n
/ritual - Получить задание на сегодня.
/magicball - Задать вопрос шару предсказаний.
/history – Посмотреть историю твоих предсказаний.
/help - Помощь.
Бот работает с кнопками, просто нажми на нужную!\n
💡 *Совет:* Добавь бота в избранные чаты, чтобы не потерять его!
"""
    await message.answer(help_text, parse_mode="Markdown")

@dp.message()
async def handle_buttons(message: Message, state: FSMContext):
    if message.text == "🔮 Получить предсказание":
        await send_prediction(message)
    elif message.text == "🔄 История предсказаний":
        await show_history(message)
    elif message.text == "✨ Узнать уровень магической энергии":
        await magic_command(message)
    elif message.text == "🎲 Проверить удачу":
        await luck_index(message)
    elif message.text == "🧙‍♂️ Вопрос от Оракула":
        await oracle_question(message, state)
    elif message.text == "📜 Ежедневный ритуал":
        await daily_ritual(message)
    elif message.text == "ℹ️ Помощь":
        await send_help(message)
    elif message.text == "🎱 Шар предсказаний":
        await start_magic_ball(message, state)
    else:
        await message.answer("Я не понимаю эту команду. Попробуй нажать на кнопку! 😊")


async def main():
    """Запуск бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())