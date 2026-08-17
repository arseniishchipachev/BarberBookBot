from .dto import BarberDTO, BookingDTO, ServiceDTO

class FakeBarberRepository:
    def __init__(self):
        self._barbers = [
            BarberDTO(id = 1, name='Леха', description='Топовый мастер по фейдам', number='+78005684741', is_available=True),
            BarberDTO(id=2, name='Игорь', description='Эксперт по оформлению бороды', number='+79004484732',is_available=True),
            BarberDTO(id=1, name='Иван', description='Классические стрижки', number='+78807784789',is_available=False),
        ]
        self._bookings = []

    async def get_active_barbers(self) -> list[BarberDTO]:
        return [b for b in self._barbers if b.is_available]

    async def get_barber_by_id(self, barber_id: int) -> BarberDTO | None:
        for b in self._barbers:
            if b.id == barber_id:
                return b

    async def add_booking(self, booking: BookingDTO) -> bool:
        self._bookings.append(booking)
        print(f"[MOCK DB] Добавлена новая запись: {booking}")
        return True

barber_repo = FakeBarberRepository()

class FakeServiceRepository:
    def __init__(self):
        self._services = [
            ServiceDTO(id=1,category_services= 'haircut', service_name='Мужская стрижка', description='классика (ножницы + машинка), мытье головы, стайлинг.', price=1800),
            ServiceDTO(id=2,category_services= 'haircut', service_name='Стрижка машинкой', description='простая стрижка под 1–2 насадки.', price=1000),
            ServiceDTO(id=3,category_services= 'haircut', service_name='Стрижка удлиненных волос', description='для каре и длинных стрижек, требует больше времени.', price=2200),
            ServiceDTO(id=4,category_services= 'haircut', service_name='Детская стрижка', description='обычно для парней до 12 лет.', price=1400),
            ServiceDTO(id=5,category_services= 'haircut', service_name='Камуфляж седины', description='быстрое тонирование волос, не полноценное окрашивание.', price=1200),
            ServiceDTO(id=6,category_services= 'beard', service_name='Моделирование бороды', description='создание формы, стрижка триммером и ножницами.', price=1200),
            ServiceDTO(id=7,category_services= 'beard', service_name='Королевское бритье', description='распаривание горячим полотенцем и бритье опасной бритвой.', price=1600),
            ServiceDTO(id=8,category_services= 'beard', service_name='Камуфляж бороды', description='выравнивание цвета бороды, скрытие проплешин или седины.', price=1000),
            ServiceDTO(id=9, category_services='category_care_packages', service_name='Удаление волос воском', description='убираются лишние волосы в носу, ушах и на межбровье.', price=500),
            ServiceDTO(id=10, category_services='category_care_packages', service_name='Черная маска / Пилинг', description='глубокое очищение пор лица.', price=800),
            ServiceDTO(id=11, category_services='category_care_packages', service_name='Патчи под глаза', description='экспресс-уход во время стрижки для снятия усталости.', price=400),
            ServiceDTO(id=12, category_services='category_care_packages', service_name='Комплекс «Стрижка + Борода»', description='самая популярная позиция в любом барбершопе, выгоднее, чем отдельно', price=2600),
            ServiceDTO(id=13, category_services='category_care_packages', service_name='Комплекс «Отец + Сын', description='парная стрижка.', price=2800),
            ServiceDTO(id=14, category_services='category_care_packages', service_name='Комплекс «Все включено»', description='стрижка, борода, уход за лицом и воск.', price=3500),
        ]

    async def get_all_services(self) -> list[ServiceDTO]:
        return self._services

    async def get_service_by_id(self, service_id: int) -> ServiceDTO | None:
        for s in self._services:
            if s.id == service_id:
                return s
        return None

    async def get_services_by_category(self, category_code: str) -> list[ServiceDTO]:
        return [s for s in self._services if s.category_services == category_code]

service_repo = FakeServiceRepository()


