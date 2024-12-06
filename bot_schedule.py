import logging, asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import aioschedule
from datetime import datetime
from keyboard import get_main_menu, get_time_keyboard, get_schedule_keyboard
from config import token
from aiogram.exceptions import TelegramBadRequest
from aiogram import Router

logging.basicConfig(level=logging.INFO)

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())

users_data = {}

@dp.message(Command("start"))
async def start_command(message: Message):
    user_id = message.from_user.id
    if user_id not in users_data:
        users_data[user_id] = []
        await message.answer("Вы зарегистрированы! Используйте меню ниже для управления расписанием.", reply_markup=get_main_menu())
    else:
        await message.answer("Добро пожаловать обратно! Используйте меню ниже для управления расписанием.", reply_markup=get_main_menu())

@dp.callback_query(lambda callback: callback.data.startswith("menu_"))
async def handle_main_menu(callback_query: CallbackQuery):
    action = callback_query.data.split("_")[1]
    user_id = callback_query.from_user.id

    if action == "set_schedule":
        await bot.send_message(user_id, "Выберите время для напоминания:", reply_markup=get_time_keyboard())
    elif action == "view_schedule":
        schedule = users_data.get(user_id, [])
        if schedule:
            await bot.send_message(user_id, "Ваше расписание:\n" + "\n".join(schedule), reply_markup=get_main_menu())
        else:
            await bot.send_message(user_id, "Ваше расписание пусто.", reply_markup=get_main_menu())
    elif action == "delete_schedule":
        schedule = users_data.get(user_id, [])
        if schedule:
            await bot.send_message(user_id, "Выберите напоминание для удаления:", reply_markup=get_schedule_keyboard(schedule))
        else:
            await bot.send_message(user_id, "Ваше расписание пусто.", reply_markup=get_main_menu())
    elif action == "update_schedule":
        schedule = users_data.get(user_id, [])
        if schedule:
            await bot.send_message(user_id, "Выберите напоминание для изменения:", reply_markup=get_schedule_keyboard(schedule))
        else:
            await bot.send_message(user_id, "Ваше расписание пусто.", reply_markup=get_main_menu())
    await callback_query.answer()

@dp.callback_query(lambda callback: callback.data.startswith("time_"))
async def handle_time_selection(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_time = callback_query.data.split("_")[1]
    if user_id not in users_data:
        users_data[user_id] = []
    users_data[user_id].append(selected_time)
    await callback_query.answer()
    await bot.send_message(user_id, f"Напоминание установлено на {selected_time}.", reply_markup=get_main_menu())

@dp.callback_query(lambda callback: callback.data.startswith("schedule_"))
async def handle_schedule_action(callback_query: CallbackQuery):
    user_id = callback_query.from_user.id
    selected_time = callback_query.data.split("_")[1]

    if selected_time in users_data.get(user_id, []):
        users_data[user_id].remove(selected_time)
        await bot.send_message(user_id, f"Напоминание на {selected_time} удалено.", reply_markup=get_main_menu())
    else:
        await bot.send_message(user_id, "Напоминание не найдено.", reply_markup=get_main_menu())
    await callback_query.answer()

async def send_notifications():
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    for user_id, schedule in users_data.items():
        if current_time in schedule:
            await bot.send_message(user_id, "Пора выполнить задачу!")

async def scheduler():
    aioschedule.every().minute.do(send_notifications)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

async def main():
    dp.include_router(dp.router)
    asyncio.create_task(scheduler())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)
    try:
        chat_id = users_data['chat_id']
        logging.debug(f"Айди: {chat_id}")
        await bot.send_message(chat_id, f"Задание для {users_data['name']} выполнено")
    except TelegramBadRequest as e:
        logging.error(f"Ошибка: {e}")

if __name__ == "__main__":
    asyncio.run(main())