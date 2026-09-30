from sqlalchemy import select, func
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Barber, Service, ServiceCategory, Appointment, User
from .dto import BarberDTO, BookingDTO, ServiceDTO, UserDTO


class BarberRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_active_barbers(self) -> list[BarberDTO]:
        """Получить всех активных мастеров."""
        query = select(Barber).where(Barber.is_available.is_(True))
        result = await self.session.scalars(query)
        barbers = result.all()

        return [
            BarberDTO(
                id=b.id,
                name=b.full_name,
                description=b.description or "",
                number=b.phone,
                is_available=b.is_available,
            )
            for b in barbers
        ]

    async def get_barber_by_id(self, barber_id: int) -> BarberDTO | None:
        """Получить мастера по его ID."""
        barber = await self.session.get(Barber, barber_id)
        if not barber:
            return None

        return BarberDTO(
            id=barber.id,
            name=barber.full_name,
            description=barber.description or "",
            number=barber.phone,
            is_available=barber.is_available,
        )

    async def add_booking(self, booking: BookingDTO) -> bool:
        """Сохранить бронирование в таблицу appointments."""
        new_appointment = Appointment(
            user_id=booking.user_id,
            barber_id=booking.barber_id,
            service_id=booking.service_id,
            appointment_date=booking.date_time,
            status="confirmed",
        )
        self.session.add(new_appointment)
        await self.session.flush()
        return True

    async def get_user_bookings(self, user_id: int):
        """Возвращает список активных записей пользователя вместе с инфой о мастере и услуге."""
        stmt = (
            select(Appointment, Barber, Service)
            .join(Barber, Appointment.barber_id == Barber.id)
            .join(Service, Appointment.service_id == Service.id)
            .where(Appointment.user_id == user_id)
            .order_by(Appointment.appointment_date.desc())
        )
        result = await self.session.execute(stmt)
        return result.all()

    async def get_booking_slots(self, barber_id: int, target_date: date) -> list[str]:
        """Возвращает список занятых часов (например, ['11:00', '15:00']) на выбранный день."""
        stmt = (
            select(Appointment.appointment_date).where(
                Appointment.barber_id == barber_id,
                func.date(Appointment.appointment_date) == target_date
            )
        )

        result = await self.session.execute(stmt)
        booked_datetimes = result.scalars().all()
        return [dt.strftime("%H:%M") for dt in booked_datetimes]

    async def delete_booking(self, booking_id: int, user_id: int) -> bool:
        """Удаляет запись пользователя по ID."""
        stmt = select(Appointment).where(
            Appointment.id == booking_id,
            Appointment.user_id == user_id
        )
        result = await self.session.execute(stmt)
        booking = result.scalar_one_or_none()

        if booking:
            await self.session.delete(booking)
            await self.session.flush()
            return True
        return False

class ServiceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_all_services(self) -> list[ServiceDTO]:
        """Получить все услуги с жадной загрузкой их категорий."""
        query = select(Service).options(selectinload(Service.category))
        result = await self.session.scalars(query)
        services = result.all()

        return [
            ServiceDTO(
                id=s.id,
                category_services=s.category.name_category,
                service_name=s.service_name,
                description=s.description or "",
                price=s.price,
            )
            for s in services
        ]

    async def get_service_by_id(self, service_id: int) -> ServiceDTO | None:
        """Получить услугу по её ID."""
        query = (
            select(Service)
            .where(Service.id == service_id)
            .options(selectinload(Service.category))
        )
        service = await self.session.scalar(query)
        if not service:
            return None

        return ServiceDTO(
            id=service.id,
            category_services=service.category.name_category,
            service_name=service.service_name,
            description=service.description or "",
            price=service.price,
        )

    async def get_services_by_category(self, category_code: str) -> list[ServiceDTO]:
        """Получить услуги конкретной категории (haircut, beard и т.д.)."""
        query = (
            select(Service)
            .join(Service.category)
            .where(ServiceCategory.name_category == category_code)
            .options(selectinload(Service.category))
        )
        result = await self.session.scalars(query)
        services = result.all()

        return [
            ServiceDTO(
                id=s.id,
                category_services=category_code,
                service_name=s.service_name,
                description=s.description or "",
                price=s.price,
            )
            for s in services
        ]

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, tg_id: int) -> UserDTO | None:
        """Поиск пользователя по Telegram ID."""
        user = await self.session.get(User, tg_id)
        if not user:
            return None
        return UserDTO(
            id=user.id,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at,
        )

    async def get_or_create(
            self, tg_id: int, full_name: str, phone: str | None = None
    ) -> UserDTO:
        """
        Получает пользователя из БД. Если его нет — регистрирует.
        Если имя изменилось в Telegram — обновляет его.
        """
        user = await self.session.get(User, tg_id)

        if not user:
            user = User(
                id=tg_id,
                full_name=full_name,
                phone=phone,
            )
            self.session.add(user)
            await self.session.flush()
        else:
            # Актуализируем имя, если юзер сменил его в профиле Telegram
            if user.full_name != full_name:
                user.full_name = full_name
            if phone and not user.phone:
                user.phone = phone
            await self.session.flush()

        return UserDTO(
            id=user.id,
            full_name=user.full_name,
            phone=user.phone,
            created_at=user.created_at,
        )

    async def update_phone(self, tg_id: int, phone: str) -> bool:
        """Обновляет номер телефона пользователя."""
        user = await self.session.get(User, tg_id)
        if not user:
            return False
        user.phone = phone
        await self.session.flush()
        return True