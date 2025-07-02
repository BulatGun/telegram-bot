import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import os

API_TOKEN = "7670502098:AAHJ3IIrJi1v6S9dPDNBCSTNBH6OKPVre90"
USER_IDS = [490752709, 479261771]

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
scheduler = AsyncIOScheduler(timezone='Europe/Moscow')

COUNTER_FILE = 'days_counter.txt'

def get_days_count():
    if not os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'w') as f:
            f.write('0')
        return 0
    with open(COUNTER_FILE, 'r') as f:
        return int(f.read().strip())

def set_days_count(value):
    with open(COUNTER_FILE, 'w') as f:
        f.write(str(value))

def increment_days_count():
    days = get_days_count() + 1
    set_days_count(days)
    return days

async def send_reminder():
    days = get_days_count()
    text = f"бро, сегодня полюбому нужно выложить шортсы. У тебя стрик из {days} дней"
    for user_id in USER_IDS:
        await bot.send_message(user_id, text)

async def send_check():
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton("✅ Да", callback_data="done_yes"),
        InlineKeyboardButton("❌ Нет", callback_data="done_no")
    )
    text = "бро, ты выложил вчера шортсы?"
    for user_id in USER_IDS:
        await bot.send_message(user_id, text, reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data in ['done_yes', 'done_no'])
async def process_callback(callback_query: types.CallbackQuery):
    if callback_query.data == 'done_yes':
        days = increment_days_count()
        await bot.answer_callback_query(callback_query.id, text=f"Красава! Стрик теперь {days} дней.")
        await bot.send_message(callback_query.from_user.id, f"🔥 Бро, стрик теперь {days} дней!")
    else:
        set_days_count(0)
        await bot.answer_callback_query(callback_query.id, text="Счётчик сброшен.")
        await bot.send_message(callback_query.from_user.id, "💀 Стрик обнулён. Начинаем заново!")

async def on_startup(_):
    scheduler.add_job(send_reminder, 'cron', hour=21, minute=0)
    scheduler.add_job(send_check, 'cron', hour=9, minute=0)
    scheduler.start()

async def main():
    await on_startup(None)
    await dp.start_polling()

if __name__ == '__main__':
    asyncio.run(main())

