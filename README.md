# 🔮 Bot Prediction — Магический Оракул в Telegram

## Ссылка на бота
[Перейти в Telegram](https://t.me/bredskazatel_bot)

## Описание проекта
Этот Telegram-бот предсказывает будущее, задаёт философские вопросы, оценивает уровень удачи и магии, а также даёт ежедневные ритуалы.  
Поддерживает кнопки для удобного взаимодействия и хранит историю предсказаний.  

## Функционал
- **Получение предсказаний** — случайные предсказания дня.
- **Оракул** — задаёт философский вопрос и даёт загадочный ответ.
- **Шар предсказаний** — отвечает на вопросы в стиле магического шара 8-ball.
- **Магическая энергия** — проверка уровня магии (раз в день).
- **Индекс удачи** — оценивает, насколько удачный будет день.
- **Ежедневный ритуал** — выдаёт небольшие задания для саморазвития.
- **История предсказаний** — хранит последние предсказания.

## Технологии
- Python 3.10+
- Aiogram 3.x — асинхронный Telegram API
- Python-dotenv — работа с переменными окружения
- Defaultdict — удобное хранение данных
- FSM (Finite State Machine) — обработка состояний пользователя

## Структура проекта

```
bot_prediction/
│── main.py                  # Основной код бота
│── .env                     # Переменные окружения (не загружаются в Git)
│── requirements.txt         # Список зависимостей
│── README.md                # Документация проекта
│── daily_rituals.txt        # База ежедневных ритуалов
│── predictions.txt          # База предсказаний
│── oracle_questions.txt     # База философских вопросов
│── magic_ball_responses.txt # База ответов шара предсказаний
│── oracle_responses.txt     # База обобщённых ответов Оракула
```


Этот бот разработан с любовью к шуточным предсказаниям.
Если у вас есть вопросы или предложения — пишите! 😉


