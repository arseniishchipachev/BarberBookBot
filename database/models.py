from sqlalchemy import BigInteger, Boolean, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, relationship, mapped_column
from datetime import datetime
from database.database import Base

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=False)
    full_name: Mapped[str] = mapped_column(String(128))
    phone: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="user")

class Barber(Base):
    __tablename__ = 'barbers'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(128))
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    phone: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    is_available: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    appointments: Mapped[list["Appointment"]] = relationship(back_populates="barber")

class ServiceCategory(Base):
    __tablename__ = 'category_services'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name_category: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    services: Mapped[list["Service"]] = relationship(back_populates="category")


class Service(Base):
    __tablename__ = 'services'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    service_name: Mapped[str] = mapped_column(String(128), unique=True, nullable=False)
    description: Mapped[str | None] = mapped_column(String(256), nullable=True)
    price: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    category_services_id: Mapped[int] = mapped_column(BigInteger, ForeignKey('category_services.id'))

    category: Mapped["ServiceCategory"] = relationship(back_populates="services")
    appointments: Mapped[list["Appointment"]] = relationship(back_populates="service")

class Appointment(Base):
    __tablename__ = 'appointments'

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.id"))
    barber_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("barbers.id"))
    service_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("services.id"))

    appointment_date: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="confirmed")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="appointments")
    barber: Mapped["Barber"] = relationship(back_populates="appointments")
    service: Mapped["Service"] = relationship(back_populates="appointments")
