from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession]:
    """
        Асинхронный генератор, предоставляющий сессию подключения к базе данных.

        Используется как зависимость (`Depends(get_db)`) во всех маршрутах FastAPI, где требуется работа с БД.

        Возвращает:
            AsyncGenerator[AsyncSession, None]: Асинхронная сессия SQLAlchemy.
        """
    # Контекстный менеджер создаёт асинхронную сессию и автоматически её закрывает после использования
    async with async_session_maker as session:
        # Возвращает сессию наружу — вызывающий код может выполнять запросы к БД
        yield session
