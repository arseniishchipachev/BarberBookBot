from datetime import date, timedelta
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from database.dto import BarberDTO, ServiceDTO

WORKING_HOURS = [f"{hour:02d}:00" for hour in range(10, 22)]

main_menu_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✂️ Выбрать услугу", callback_data="show_services"),
            InlineKeyboardButton(text="📅 Мои записи", callback_data="my_bookings"),
        ],
        [
            InlineKeyboardButton(text="🧔 Наши барберы", callback_data="show_team"),
            InlineKeyboardButton(text="📍 Контакты и инфо", callback_data="show_info"),
        ]
    ]
)

check_book_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="✂️ Записаться", callback_data="show_services")],
        [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu")]
    ]
)

services_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✂️ Волосы", callback_data="haircut"),
            InlineKeyboardButton(text="🧔 Борода", callback_data="beard"),
        ],
        [
            InlineKeyboardButton(text="🧴 Уход и Комплексы", callback_data="category_care_packages"),
            InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu"),
        ]
    ]
)

show_info_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu")]
    ]
)


def get_barber_kb(barbers: list[BarberDTO]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for barber in barbers:
        builder.row(InlineKeyboardButton(text=barber.name, callback_data=f"select_barber:{barber.id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад к услугам", callback_data="back_to_category"))
    builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu"))
    return builder.as_markup()


def get_services_kb(services: list[ServiceDTO]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for service in services:
        builder.row(InlineKeyboardButton(
            text=f"{service.service_name} — {service.price} ₽",
            callback_data=f"select_service:{service.id}"
        ))
    builder.row(InlineKeyboardButton(text="⬅️ Назад к категориям", callback_data="show_services"))
    return builder.as_markup()


def get_final_booking_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Подтвердить", callback_data="confirm_booking"),
        InlineKeyboardButton(text="❌ Отменить", callback_data="cancel_booking")
    )
    builder.row(InlineKeyboardButton(text="⬅️ Назад к выбору даты", callback_data="back_to_dates"))
    return builder.as_markup()


def get_team_showcase_kb(barbers: list[BarberDTO]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for barber in barbers:
        builder.row(InlineKeyboardButton(text=barber.name, callback_data=f"show_barber_info:{barber.id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu"))
    return builder.as_markup()


def get_barber_profile_kb(barber_id: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📅 Записаться к мастеру", callback_data=f"book_with_barber:{barber_id}"))
    builder.row(InlineKeyboardButton(text="⬅️ Назад к мастерам", callback_data="show_team"))
    return builder.as_markup()


def get_user_bookings_kb(bookings) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for appointment, barber, service in bookings:
        builder.row(InlineKeyboardButton(
            text=f"❌ Отменить: {service.service_name}",
            callback_data=f"cancel_user_booking:{appointment.id}"
        ))
    builder.row(
        InlineKeyboardButton(text="✂️ Записаться ещё", callback_data="show_services"),
        InlineKeyboardButton(text="⬅️ Главное меню", callback_data="to_main_menu")
    )
    return builder.as_markup()


def get_dates_kb(week_offset: int = 0) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    today = date.today()
    start_day = today + timedelta(days=week_offset * 5)

    for i in range(5):
        day = start_day + timedelta(days=i)
        day_str = day.strftime("%Y-%m-%d")
        day_month = day.strftime("%d.%m")

        if day == today:
            label = f"Сегодня ({day_month})"
        elif day == today + timedelta(days=1):
            label = f"Завтра ({day_month})"
        else:
            label = day.strftime("%d.%m (%a)")

        builder.row(InlineKeyboardButton(text=f"📅 {label}", callback_data=f"select_date:{day_str}"))

    nav_buttons = []
    if week_offset > 0:
        nav_buttons.append(InlineKeyboardButton(text="⬅️ Раньше", callback_data=f"dates_page:{week_offset - 1}"))
    if week_offset < 3:
        nav_buttons.append(InlineKeyboardButton(text="Позже ➡️", callback_data=f"dates_page:{week_offset + 1}"))

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.row(InlineKeyboardButton(text="⬅️ Назад к мастерам", callback_data="back_to_barbers"))
    return builder.as_markup()


def get_time_slots_kb(booked_slots: list[str]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    free_slots = [slot for slot in WORKING_HOURS if slot not in booked_slots]

    for slot in free_slots:
        builder.add(InlineKeyboardButton(text=f"🕒 {slot}", callback_data=f"select_time:{slot}"))

    builder.adjust(3)
    builder.row(InlineKeyboardButton(text="⬅️ Выбрать другой день", callback_data="back_to_dates"))
    return builder.as_markup()