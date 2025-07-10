from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase  # Базовый класс для создания ORM моделей

# Создание асинхронного движка
# шаблон - myusername:mypassword@myhost:5432/mydatabase
engine = create_async_engine(
    'postgresql+asyncpg://postgres:postgres@localhost:5432/ecommerce',
    echo=True   # Включает вывод SQL-запросов в консоль (для отладки)
)

# Фабрика для создания асинхронных сессий взаимодействия с базой данных.
# expire_on_commit=False означает, что SQLAlchemy не "забудет" значения полей объектов после commit()
# и не будет автоматически повторно запрашивать их из базы данных при следующем обращении.
# class_=AsyncSession — тип создаваемой сессии
async_session_maker = async_sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

# Базовый класс для всех ORM-моделей в проекте
# Все модели таблиц должны наследовать от него, чтобы SQLAlchemy понимал структуру
class Base(DeclarativeBase):
    pass
