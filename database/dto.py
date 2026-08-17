from dataclasses import dataclass
from datetime import datetime

@dataclass
class BarberDTO:
    id: int
    name: str
    description: str
    number: str
    is_available: bool

@dataclass
class ServiceDTO:
    id: int
    category_services: str
    service_name: str
    description: str
    price: int

@dataclass
class BookingDTO:
    id: int
    user_id: int
    barber_id: int
    service_id: int
    date_time: datetime

@dataclass
class UserDTO:
    id: int