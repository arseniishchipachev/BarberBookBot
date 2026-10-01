import asyncio
from sqlalchemy import select
from database.database import engine, Base, async_session_maker
from database.models import Barber, ServiceCategory, Service, User, Appointment


async def init_db():
    async with engine.begin() as conn:
        print("Создание таблиц в PostgreSQL...")
        await conn.run_sync(Base.metadata.create_all)
        print("Таблицы успешно созданы!")

    async with async_session_maker() as session:
        existing_categories = await session.scalars(select(ServiceCategory))
        if existing_categories.first():
            print("База уже наполнена данными. Пропускаем сидинг.")
            return

        print("Наполнение базы начальными данными...")

        cat_haircut = ServiceCategory(name_category="haircut")
        cat_beard = ServiceCategory(name_category="beard")
        cat_packages = ServiceCategory(name_category="category_care_packages")

        session.add_all([cat_haircut, cat_beard, cat_packages])
        await session.flush()

        services = [
            Service(
                category_services_id=cat_haircut.id,
                service_name="Мужская стрижка",
                description="классика (ножницы + машинка), мытье головы, стайлинг.",
                price=1800,
            ),
            Service(
                category_services_id=cat_haircut.id,
                service_name="Стрижка машинкой",
                description="простая стрижка под 1–2 насадки.",
                price=1000,
            ),
            Service(
                category_services_id=cat_haircut.id,
                service_name="Стрижка удлиненных волос",
                description="для каре и длинных стрижек, требует больше времени.",
                price=2200,
            ),
            Service(
                category_services_id=cat_haircut.id,
                service_name="Детская стрижка",
                description="обычно для парней до 12 лет.",
                price=1400,
            ),
            Service(
                category_services_id=cat_haircut.id,
                service_name="Камуфляж седины",
                description="быстрое тонирование волос, не полноценное окрашивание.",
                price=1200,
            ),
            Service(
                category_services_id=cat_beard.id,
                service_name="Моделирование бороды",
                description="создание формы, стрижка триммером и ножницами.",
                price=1200,
            ),
            Service(
                category_services_id=cat_beard.id,
                service_name="Королевское бритье",
                description="распаривание горячим полотенцем и бритье опасной бритвой.",
                price=1600,
            ),
            Service(
                category_services_id=cat_beard.id,
                service_name="Камуфляж бороды",
                description="выравнивание цвета бороды, скрытие проплешин или седины.",
                price=1000,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Удаление волос воском",
                description="убираются лишние волосы в носу, ушах и на межбровье.",
                price=500,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Черная маска / Пилинг",
                description="глубокое очищение пор лица.",
                price=800,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Патчи под глаза",
                description="экспресс-уход во время стрижки для снятия усталости.",
                price=400,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Комплекс «Стрижка + Борода»",
                description="самая популярная позиция в любом барбершопе, выгоднее, чем отдельно",
                price=2600,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Комплекс «Отец + Сын»",
                description="парная стрижка.",
                price=2800,
            ),
            Service(
                category_services_id=cat_packages.id,
                service_name="Комплекс «Все включено»",
                description="стрижка, борода, уход за лицом и воск.",
                price=3500,
            ),
        ]
        session.add_all(services)

        barbers = [
            Barber(
                full_name="Алексей",
                description="Топовый мастер по фейдам",
                phone="+78005684741",
                is_available=True,
            ),
            Barber(
                full_name="Игорь",
                description="Эксперт по оформлению бороды",
                phone="+79004484732",
                is_available=True,
            ),
            Barber(
                full_name="Иван",
                description="Классические стрижки",
                phone="+78807784789",
                is_available=False,
            ),
        ]
        session.add_all(barbers)

        await session.commit()
        print("База успешно заполнена данными!")


if __name__ == "__main__":
    asyncio.run(init_db())