from datetime import datetime
from aiogram import types, Router, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from database.dto import BookingDTO
from database.repository import BarberRepository, ServiceRepository, UserRepository
from handlers.states import BookingState
from keyboards.reply_keyboard import main_kb as reply_main_kb
from keyboards.inlinekeyboards import main_menu_kb as inline_main_kb
from keyboards.inlinekeyboards import services_kb as inline_services_kb
from keyboards.inlinekeyboards import show_info_kb as inline_show_info_kb
from keyboards.inlinekeyboards import (
    get_barber_kb,
    get_services_kb,
    get_final_booking_kb,
    check_book_kb,
    get_team_showcase_kb,
    get_barber_profile_kb,
    get_user_bookings_kb,
    get_dates_kb,
    get_time_slots_kb
)

user_private_router = Router()


@user_private_router.message(CommandStart())
async def command_start(message: types.Message, session: AsyncSession):
    user_repo = UserRepository(session)
    await user_repo.get_or_create(
        tg_id=message.from_user.id,
        full_name=message.from_user.full_name,
    )
    await message.answer(
        "👋 Привет! Я BarberBook Bot — твой личный помощник для быстрой записи на стрижку и уход.\n\n"
        "Здесь ты можешь выбрать своего мастера, определиться с услугой и занять удобное время всего за пару кликов.\n\n"
        "👇 Нажми кнопку ниже, чтобы начать!",
        reply_markup=reply_main_kb
    )


@user_private_router.message(F.text == '🏠 Главное меню')
async def command_main_menu(message: types.Message):
    await message.answer(
        "Здесь ты можешь выбрать интересующую тебя услугу и проверить свои актуальные записи к барберу\n\n"
        "👇 <b>Выбери нужное действие:</b>",
        reply_markup=inline_main_kb
    )


@user_private_router.callback_query(F.data == 'to_main_menu')
async def process_to_main_menu(callback: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(
        text="Здесь ты можешь выбрать интересующую тебя услугу и проверить свои актуальные записи:\n\n👇 <b>Выбери нужное действие:</b>",
        reply_markup=inline_main_kb
    )
    await callback.answer()


@user_private_router.callback_query(F.data == 'my_bookings')
async def process_book_now(callback: types.CallbackQuery, session: AsyncSession):
    barber_repo = BarberRepository(session)
    bookings = await barber_repo.get_user_bookings(callback.from_user.id)
    if not bookings:
        await callback.message.edit_text(
            text="На данный момент у вас нет активных записей.",
            reply_markup=check_book_kb
        )
        await callback.answer()
        return

    text_lines = ["📋 <b>Ваши актуальные записи:</b>\n"]
    for appointment, barber, service in bookings:
        formatted_date = appointment.appointment_date.strftime("%d.%m.%Y в %H:%M")
        text_lines.append(
            f"▫️ <b>Услуга:</b> {service.service_name} ({service.price} ₽)\n"
            f"💈 <b>Барбер:</b> {barber.full_name}\n"
            f"📅 <b>Время:</b> {formatted_date}\n"
        )
    text_lines.append("👇 <i>Нажмите на кнопку ниже, чтобы отменить запись:</i>")

    await callback.message.edit_text(
        text="\n".join(text_lines),
        reply_markup=get_user_bookings_kb(bookings)
    )
    await callback.answer()


@user_private_router.callback_query(F.data.startswith('cancel_user_booking:'))
async def cancel_user_booking(callback: types.CallbackQuery, session: AsyncSession):
    booking_id = int(callback.data.split(':')[1])
    barber_repo = BarberRepository(session)

    success = await barber_repo.delete_booking(booking_id, callback.from_user.id)
    if success:
        await callback.answer("✅ Запись успешно отменена!", show_alert=True)
        await process_book_now(callback, session)
    else:
        await callback.answer("❌ Не удалось найти или отменить запись.", show_alert=True)


@user_private_router.callback_query(StateFilter(None, BookingState.choosing_service), F.data == 'show_services')
async def show_services(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookingState.choosing_category)
    await callback.message.edit_text(
        "🗂 Каталог услуг\n\n"
        "Мы разделили наш прайс на удобные категории. Выбери нужный раздел, чтобы посмотреть доступные услуги и цены.\n\n"
        "👇 Выбери категорию:",
        reply_markup=inline_services_kb
    )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_category, F.data.in_({'haircut', 'beard', 'category_care_packages'}))
async def haircut(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    category_code = callback.data
    await state.update_data(category=category_code)
    await state.set_state(BookingState.choosing_service)

    service_repo = ServiceRepository(session)
    services = await service_repo.get_services_by_category(category_code)
    await callback.message.edit_text(
        text="👇 Выбери услугу из списка ниже:",
        reply_markup=get_services_kb(services)
    )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_service, F.data.startswith('select_service:'))
async def select_barber(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    service_id = int(callback.data.split(':')[1])
    await state.update_data(service_id=service_id)

    service_repo = ServiceRepository(session)
    service = await service_repo.get_service_by_id(service_id)
    user_data = await state.get_data()

    barber_repo = BarberRepository(session)
    if user_data.get('flow') == 'from_barber':
        await state.set_state(BookingState.choosing_date)
        await callback.message.edit_text(
            text=f"✂️ <b>Выбрана услуга:</b> {service.service_name} ({service.price} ₽)\n\n👇 <b>Выберите дату записи:</b>",
            reply_markup=get_dates_kb()
        )
    else:
        await state.set_state(BookingState.choosing_barber)
        active_barbers = await barber_repo.get_active_barbers()

        barbers_text_list = "\n".join(
            f"💈 <b>{b.name}</b> — <i>{b.description}</i>"
            for b in active_barbers
        )
        await callback.message.edit_text(
            text=f"✂️ <b>Выбрана услуга:</b> {service.service_name} ({service.price} ₽)\n\n"
                 f"<b>Наши мастера:</b>\n{barbers_text_list}\n\n"
                 f"👇 <b>Выберите мастера для записи:</b>",
            reply_markup=get_barber_kb(active_barbers)
        )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_barber, F.data == 'back_to_category')
async def back_to_services(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    category = user_data.get('category')

    await state.set_state(BookingState.choosing_service)
    service_repo = ServiceRepository(session)
    services = await service_repo.get_services_by_category(category)

    await callback.message.edit_text("👇 <b>Выберите услугу из списка ниже:</b>", reply_markup=get_services_kb(services))
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_barber, F.data.startswith('select_barber:'))
async def process_barber_selected(callback: types.CallbackQuery, state: FSMContext):
    barber_id = int(callback.data.split(':')[1])
    await state.update_data(barber_id=barber_id)
    await state.set_state(BookingState.choosing_date)

    await callback.message.edit_text(
        text="👇 <b>Выберите удобную дату:</b>",
        reply_markup=get_dates_kb()
    )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_date, F.data == 'back_to_barbers')
async def back_to_barbers(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()

    if user_data.get('flow') == 'from_barber':
        await state.set_state(BookingState.choosing_service)
        category = user_data.get("category")
        service_repo = ServiceRepository(session)
        services = await service_repo.get_services_by_category(category)
        await callback.message.edit_text(
            text="👇 <b>Выберите услугу из списка ниже:</b>",
            reply_markup=get_services_kb(services)
        )
    else:
        await state.set_state(BookingState.choosing_barber)
        barber_repo = BarberRepository(session)
        barbers = await barber_repo.get_active_barbers()
        await callback.message.edit_text(
            text="👇 <b>Выбери мастера для записи:</b>",
            reply_markup=get_barber_kb(barbers)
        )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_date, F.data.startswith('dates_page:'))
async def process_dates_pagination(callback: types.CallbackQuery):
    page = int(callback.data.split(':')[1])
    await callback.message.edit_reply_markup(reply_markup=get_dates_kb(week_offset=page))
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_date, F.data.startswith('select_date:'))
async def process_date_selected(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    date_str = callback.data.split(':')[1]
    await state.update_data(selected_date=date_str)

    data = await state.get_data()
    barber_id = data["barber_id"]
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    barber_repo = BarberRepository(session)
    booked_slots = await barber_repo.get_booking_slots(barber_id, target_date)

    await callback.message.edit_text(
        text=f"Выбрана дата: <b>{target_date.strftime('%d.%m.%Y')}</b>\nВыберите свободное время:",
        reply_markup=get_time_slots_kb(booked_slots)
    )
    await state.set_state(BookingState.choosing_time)
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_time, F.data == 'back_to_dates')
async def back_to_dates(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="👇 <b>Выберите удобную дату:</b>",
        reply_markup=get_dates_kb()
    )
    await callback.answer()


@user_private_router.callback_query(BookingState.choosing_time, F.data.startswith('select_time:'))
async def process_time_selected(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    time_str = callback.data.split(":", 1)[1]
    data = await state.get_data()

    full_datetime_str = f"{data['selected_date']} {time_str}"
    await state.update_data(booking_datetime=full_datetime_str)

    service_repo = ServiceRepository(session)
    service = await service_repo.get_service_by_id(data["service_id"])
    barber_repo = BarberRepository(session)
    barber = await barber_repo.get_barber_by_id(data["barber_id"])

    date_obj = datetime.strptime(data['selected_date'], "%Y-%m-%d")
    formatted_date = date_obj.strftime("%d.%m.%Y")

    summary_text = (
        "📋 <b>Проверьте данные вашей записи:</b>\n\n"
        f"✂️ <b>Услуга:</b> {service.service_name} ({service.price} ₽)\n"
        f"💈 <b>Мастер:</b> {barber.name}\n"
        f"📅 <b>Дата:</b> {formatted_date}\n"
        f"🕒 <b>Время:</b> {time_str}\n\n"
        "Всё верно?"
    )

    await state.set_state(BookingState.confirm_booking)
    await callback.message.edit_text(text=summary_text, reply_markup=get_final_booking_kb())
    await callback.answer()


@user_private_router.callback_query(BookingState.confirm_booking, F.data == 'confirm_booking')
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext, session: AsyncSession):
    user_data = await state.get_data()
    barber_repo = BarberRepository(session)

    booking_dt = datetime.strptime(user_data["booking_datetime"], "%Y-%m-%d %H:%M")

    booking_dto = BookingDTO(
        id=0,
        user_id=callback.from_user.id,
        barber_id=user_data["barber_id"],
        service_id=user_data["service_id"],
        date_time=booking_dt
    )
    await barber_repo.add_booking(booking_dto)

    await callback.message.edit_text(
        text=f"🎉 <b>Вы успешно записаны!</b>\n\nЖдем вас {booking_dt.strftime('%d.%m.%Y в %H:%M')}.",
        reply_markup=None
    )
    await state.clear()
    await callback.answer()


@user_private_router.callback_query(BookingState.confirm_booking, F.data == 'cancel_booking')
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text="❌ <b>Запись отменена.</b>", reply_markup=None)
    await state.clear()
    await callback.answer()


@user_private_router.callback_query(F.data == 'show_info')
async def show_info(callback: types.CallbackQuery):
    text = (
        "💈 <b>О барбершопе BarberBook</b>\n"
        "Мы — пространство стиля, комфорта и классических традиций бритья.\n\n"
        "📍 <b>Наш адрес:</b> ул. Маяковская, д. 10 (3 минуты пешком)\n"
        "⏰ <b>График работы:</b> Каждый день с 10:00 до 22:00\n"
        "📞 <b>Телефон:</b> +7 (999) 123-45-67\n\n"
        "☕ <b>Для наших гостей:</b> Зона отдыха, свежий кофе и напитки — абсолютно бесплатно!\n\n"
        "👇 <b>Связь с нами и соцсети:</b>"
    )
    await callback.message.edit_text(text=text, parse_mode="HTML", reply_markup=inline_show_info_kb)
    await callback.answer()


@user_private_router.callback_query(F.data == 'show_team')
async def start_booking_with_barber(callback: types.CallbackQuery, session: AsyncSession):
    barber_repo = BarberRepository(session)
    active_barbers = await barber_repo.get_active_barbers()
    await callback.message.edit_text(
        text="👇 Выберите мастера для записи:",
        reply_markup=get_team_showcase_kb(active_barbers)
    )
    await callback.answer()


@user_private_router.callback_query(F.data.startswith('show_barber_info:'))
async def show_barber_profile(callback: types.CallbackQuery, session: AsyncSession):
    barber_id = int(callback.data.split(':')[1])
    barber_repo = BarberRepository(session)
    barber = await barber_repo.get_barber_by_id(barber_id)

    text = (
        f"💈 <b>Мастер:</b> {barber.name}\n"
        f"ℹ️ <b>О мастере:</b> <i>{barber.description}</i>"
    )
    await callback.message.edit_text(text=text, reply_markup=get_barber_profile_kb(barber.id))
    await callback.answer()


@user_private_router.callback_query(F.data.startswith('book_with_barber:'))
async def start_booking_from_barber(callback: types.CallbackQuery, state: FSMContext):
    barber_id = int(callback.data.split(':')[1])
    await state.update_data(barber_id=barber_id, flow="from_barber")
    await state.set_state(BookingState.choosing_category)
    await callback.message.edit_text(
        text="👇 <b>Мастер выбран! Теперь выберите категорию услуг:</b>\n\n"
             "Мы разделили наш прайс на удобные категории. Выбери нужный раздел, чтобы посмотреть доступные услуги и цены.",
        reply_markup=inline_services_kb
    )
    await callback.answer()