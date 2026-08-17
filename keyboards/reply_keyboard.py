from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

MAIN_MENU_BUTTONS = [
    KeyboardButton(text="🏠 Главное меню")
]

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="🏠 Главное меню")
        ]
    ],
    resize_keyboard=True
)