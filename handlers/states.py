from aiogram.fsm.state import State, StatesGroup

class BookingState(StatesGroup):
    choosing_category = State()
    choosing_service = State()
    choosing_barber = State()
    # choosing_date = State()
    confirm_booking = State()

class AdminState(StatesGroup):
    name = State()
    description = State()
    number = State()
