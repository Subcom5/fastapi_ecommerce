from email.policy import default

from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlalchemy import select, insert
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db

# Импорт базовой HTTP авторизации (логин + пароль)
# Вызывает в браузере всплывающую форму входа, через которую мы вводим имя пользователя и пароль
security = HTTPBasic()

router = APIRouter(prefix='/auth', tags=['auth'])

# Контекст шифрования паролей: указываем использовать алгоритм bcrypt
# deprecated='auto' означает, что старые схемы считаются устаревшими
bcrypt_context = CryptContext(
    schemes=['bcrypt'],     # допустимые алгоритмы
    deprecated='auto')


async def get_current_username(
        db: Annotated[AsyncSession, Depends(get_db)],           # Получаем асинхронную сессию БД
        credentials: HTTPBasicCredentials = Depends(security)   # Извлекаем логин и пароль из заголовков HTTP
):
    """
    Функция для получения текущего пользователя по HTTPBasic авторизации
    Используется как зависимость (Depends)
    """

    # Ищем пользователя в БД по имени пользователя (username)
    user = await db.scalar(
        select(User).where(User.username == credentials.username)
    )
    # Если пользователь не найден или пароль неверен — выбрасываем ошибку 401 (Unauthorized)
    if not user or not bcrypt_context.verify(credentials.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return user

@router.get('/users/me')
async def read_current_user(user: dict = Depends(get_current_username)):
    return {'User': user}


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        created_user: CreateUser
):
    await db.execute(
        insert(User).values(
            first_name=created_user.first_name,
            last_name=created_user.last_name,
            username=created_user.username,
            email=created_user.email,
            hashed_password=bcrypt_context.hash(created_user.password)
        )
    )
    await db.commit()

    return {
        'status_code': status.HTTP_201_CREATED,
        'transactions': 'Successful'
    }
