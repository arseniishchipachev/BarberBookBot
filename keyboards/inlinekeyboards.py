from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.dto import BarberDTO, ServiceDTO

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text='✂️ Выбрать услугу', callback_data='show_services'),
        InlineKeyboardButton(text="📅 Мои записи", callback_data='my_bookings'),
         ],
        [
        InlineKeyboardButton(text="🧔 Наши барберы", callback_data='show_barbers'),
        InlineKeyboardButton(text="📍 Контакты и инфо", callback_data='show_info')
        ]
    ]
)

check_book_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        #InlineKeyboardButton(text= '❌ Отменить запись', callback_data='cancel_booking'),
        InlineKeyboardButton(text= '✂️ Записаться', callback_data='show_services'),
        ],
        [
        InlineKeyboardButton(text='⬅️ Главное меню', callback_data="to_main_menu"),
        ]
    ]
)

services_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text='✂️ Волосы', callback_data='haircut'),
        InlineKeyboardButton(text='🧔 Борода', callback_data='beard'),
        ],
        [
        InlineKeyboardButton(text='🧴 Уход и Комплексы', callback_data='category_care_packages'),
        ]
    ]
)

show_info_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
        InlineKeyboardButton(text='⬅️ Главное меню', callback_data="to_main_menu"),
        ]
    ]
)

def get_barber_kb(barbers: list[BarberDTO]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for barber in barbers:
        builder.row(InlineKeyboardButton(text=barber.name, callback_data=f"select_barber:{barber.id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu"))
    return builder.as_markup()

def get_services_kb(services: list[ServiceDTO]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.row(InlineKeyboardButton(text=f"{service.service_name} — {service.price} ₽",
                                         callback_data=f"select_service:{service.id}"))
    builder.row(InlineKeyboardButton(
        text="⬅️ Назад к категориям",
        callback_data="show_services"
    ))

    return builder.as_markup()

def get_final_booking_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text= '✅ Подтвердить', callback_data="confirm_booking"),
                InlineKeyboardButton(text= '❌ Отменить', callback_data="cancel_booking"))
    return builder.as_markup()
