from aiogram import types, Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from handlers.states import BookingState
from keyboards.reply_keyboard import main_kb as reply_main_kb
from keyboards.inlinekeyboards import main_menu_kb as inline_main_kb
from keyboards.inlinekeyboards import services_kb as inline_services_kb
from keyboards.inlinekeyboards import show_info_kb as inline_show_info_kb
from database.repository import barber_repo, service_repo
from keyboards.inlinekeyboards import get_barber_kb, get_services_kb, get_final_booking_kb, check_book_kb

user_private_router = Router()

@user_private_router.message(CommandStart())
async def command_start(message: types.Message):
    await message.answer('👋 Привет! Я BarberBook Bot — твой личный помощник для быстрой записи на стрижку и уход.\n\n'
                         ' Здесь ты можешь выбрать своего мастера, определиться с услугой и занять удобное тебе время всего за пару кликов.\n\n'
                         '👇 Нажми кнопку ниже, чтобы начать!', reply_markup=reply_main_kb)

@user_private_router.message(F.text =='🏠 Главное меню')
async def command_main_menu(message: types.Message):
    await message.answer('Здесь ты можешь выбрать интересующую тебя услугу и проверить свои актуальные записи к барберу\n\n'
                         '👇 <b>Выбери нужное действие:</b> ', reply_markup=inline_main_kb)

@user_private_router.callback_query(F.data =='to_main_menu')
async def process_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text="Здесь ты можешь выбрать интересующую тебя услугу и проверить свои актуальные записи:\n\n👇 <b>Выбери нужное действие:</b>",
        reply_markup=inline_main_kb
    )
    await callback.answer()

@user_private_router.callback_query(F.data =='my_bookings')
async def process_book_now(callback: types.CallbackQuery):
    await callback.message.edit_text(
        text = 'На данный момент у вас нет записей',
        reply_markup= check_book_kb
    )
    await callback.answer()

@user_private_router.callback_query(F.data == 'show_services')
async def show_services(callback: types.CallbackQuery, state: FSMContext):
    await state.set_state(BookingState.choosing_category)
    await callback.message.answer(f'🗂 Каталог услуг\n\nМы разделили наш прайс на удобные категории. Выбери нужный раздел, чтобы посмотреть '
                         f'доступные услуги и цены.\n\n👇 Выбери категорию:', reply_markup=inline_services_kb)
    await callback.answer()

@user_private_router.callback_query(BookingState.choosing_category, F.data.in_({'haircut', 'beard', 'category_care_packages'}))
async def haircut(callback: types.CallbackQuery, state: FSMContext):
    category_code = callback.data
    await state.update_data(category=category_code)
    await state.set_state(BookingState.choosing_service)
    services = await service_repo.get_services_by_category(category_code)
    await callback.message.edit_text(
        text="👇 Выбери услугу из списка ниже:",
        reply_markup=get_services_kb(services)
    )
    await callback.answer()

@user_private_router.callback_query(BookingState.choosing_service, F.data.startswith('select_service:'))
async def select_barber(callback: types.CallbackQuery, state: FSMContext):
    service_id = int(callback.data.split(':')[1])
    await state.update_data(service_id=service_id)
    await state.set_state(BookingState.choosing_barber)
    active_barbers = await barber_repo.get_active_barbers()
    await callback.message.edit_text(
        text="👇 Выбери мастера для записи:",
        reply_markup=get_barber_kb(active_barbers)
    )
    await callback.answer()

@user_private_router.callback_query(BookingState.choosing_barber, F.data.startswith('select_barber:'))
async def process_barber_selected(callback: types.CallbackQuery, state: FSMContext):
    barber_id = int(callback.data.split(':')[1])
    await state.update_data(barber_id=barber_id)
    await state.set_state(BookingState.confirm_booking)

    user_data = await state.get_data()
    service = await service_repo.get_service_by_id(user_data.get('service_id'))
    barber = await barber_repo.get_barber_by_id(barber_id)

    summary_text = (
        "📋 <b>Проверь данные своей записи:</b>\n\n"
        f"✂️ <b>Услуга:</b> {service.service_name} ({service.price} ₽)\n"
        f"💈 <b>Мастер:</b> {barber.name}\n"
        f"📅 <b>Дата/Время:</b> *(Заглушка: Завтра в 15:00)*\n\n"
        "Всё верно?"
    )

    await callback.message.edit_text(
        text=summary_text,
        reply_markup=get_final_booking_kb()
    )
    await callback.answer()

@user_private_router.callback_query(BookingState.confirm_booking, F.data == 'confirm_booking')
async def confirm_booking(callback: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()
    print(f'[MOCK BD] запись сохранена {user_data}')
    await callback.message.edit_text(text = '🎉 <b>Вы успешно записаны!</b>\n\nЖдем вас в назначенное время.', reply_markup=None)
    await state.clear()
    await callback.answer()

@user_private_router.callback_query(BookingState.confirm_booking, F.data == 'cancel_booking')
async def cancel_booking(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text = '❌ <b>Запись отменена.</b>', reply_markup=None)
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
        "☕️ <b>Для наших гостей:</b> Зона отдыха, свежий кофе и напитки покрепче — абсолютно бесплатно!\n\n"
        "👇 <b>Связь с нами и соцсети:</b>"
    )

    await callback.message.edit_text(
        text=text,
        parse_mode="HTML",
        reply_markup=inline_show_info_kb
    )
    await callback.answer()

@user_private_router.callback_query(F.data == 'show_barbers')
async def select_barber(callback: types.CallbackQuery):
    active_barbers = await barber_repo.get_active_barbers()
    await callback.message.answer(text="Выберите мастера для записи:",
        reply_markup=get_barber_kb(active_barbers))
    await callback.answer()
