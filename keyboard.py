from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu():
    """
    Главное меню для выбора команд.
    """
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Установить напоминание", callback_data="menu_set_schedule"))
    keyboard.add(InlineKeyboardButton("Просмотреть расписание", callback_data="menu_view_schedule"))
    keyboard.add(InlineKeyboardButton("Удалить напоминание", callback_data="menu_delete_schedule"))
    keyboard.add(InlineKeyboardButton("Обновить напоминание", callback_data="menu_update_schedule"))
    return keyboard

def get_time_keyboard():
    """
    Клавиатура для выбора времени напоминания.
    """
    keyboard = InlineKeyboardMarkup(row_width=4)
    for hour in range(0, 24):
        for minute in [0, 30]:
            time_button = InlineKeyboardButton(
                f"{hour:02d}:{minute:02d}", callback_data=f"time_{hour:02d}:{minute:02d}"
            )
            keyboard.add(time_button)
    return keyboard

def get_schedule_keyboard(schedule):
    """
    Генерация клавиатуры для работы с расписанием.
    """
    keyboard = InlineKeyboardMarkup()
    for time in schedule:
        keyboard.add(InlineKeyboardButton(time, callback_data=f"schedule_{time}"))
    return keyboard
