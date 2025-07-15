from fastapi import APIRouter, Depends, status, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import insert, select
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt

from app.models.user import User
from app.schemas import CreateUser
from app.backend.db_depends import get_db


# (.venv) subcom@cspbw143:~/PycharmProjects/fastapi_ecommerce$ openssl rand -hex 32
SECRET_KEY = '0c01b525cf7df299e041c67653d9ef7cc0f9db9f3f281e27f5dcc255b049b539'
ALGORITHM = 'HS256'


# Создание маршрутизатора с префиксом /auth и тегом 'auth'
router = APIRouter(prefix='/auth', tags=['auth'])

# Схема авторизации OAuth2 (ожидает токен по пути /auth/token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')

# Контекст шифрования паролей: указываем использовать алгоритм bcrypt
# deprecated='auto' означает, что старые схемы считаются устаревшими
bcrypt_context = CryptContext(
    schemes=['bcrypt'],     # допустимые алгоритмы
    deprecated='auto')


async def authenticate_user(db: Annotated[AsyncSession, Depends(get_db)], username: str, password: str):
    """
    Проверяет, существует ли пользователь с заданным именем и паролем.
    """
    user = await db.scalar(select(User).where(User.username == username))
    if not user or not bcrypt_context.verify(password, user.hashed_password) or user.is_active == False:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Invalid authentication credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return user


async def create_access_token(
        username: str,
        user_id: int,
        is_admin: bool,
        is_supplier: bool,
        is_customer: bool,
        expires_delta: timedelta
):
    """
    Создаёт JWT-токен с данными пользователя и временем жизни.
    """
    payload = {
         'sub': username,
         'id': user_id,
         'is_admin': is_admin,
         'is_supplier': is_supplier,
         'is_customer': is_customer,
         'exp': datetime.now(timezone.utc) + expires_delta
     }
    # Преобразование datetime в timestamp (количество секунд с начала эпохи)
    payload['exp'] = int(payload['exp'].timestamp())
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    """
    Декодирует токен и извлекает информацию о текущем пользователе.
    Вызывает исключение, если токен некорректный или устарел.
    """
    try:
        # Расшифровываем токен и получаем полезную нагрузку
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get('sub')
        user_id: int | None = payload.get('id')
        is_admin: bool | None = payload.get('is_admin')
        is_supplier: bool | None = payload.get('is_supplier')
        is_customer: bool | None = payload.get('is_customer')
        expire: int | None = payload.get('exp')

        # Проверяем наличие обязательных полей
        if username is None or user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Could not validate user'
            )

        if expire is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='No access token supplied'
            )

        if not isinstance(expire, int):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Invalid token format'
            )

        # Проверка срока действия токена
        current_time = datetime.now(timezone.utc).timestamp()

        if expire < current_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail='Token expired!'
            )

        return {
            'username': username,
            'id': user_id,
            'is_admin': is_admin,
            'is_supplier': is_supplier,
            'is_customer': is_customer,
        }
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired!'
        )
    except jwt.exceptions:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate user'
        )


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        created_user: CreateUser
):
    """
    Регистрирует нового пользователя: хеширует пароль и сохраняет данные в базу.
    """
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


@router.post('/token')
async def login(
        db: Annotated[AsyncSession, Depends(get_db)],
        form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
):
    """
    Авторизует пользователя, проверяя имя и пароль.
    Возвращает JWT-токен при успешной авторизации.
    """
    user = await authenticate_user(db, form_data.username, form_data.password)
    token = await create_access_token(user.username,
                                      user.id,
                                      user.is_admin,
                                      user.is_supplier,
                                      user.is_customer,
                                      expires_delta=timedelta(minutes=20)
                                      )

    return {
        'access_token': token,
        'token_type': 'bearer'
    }


@router.get('/read_current_user')
async def read_current_user(user: str = Depends(get_current_user)):
    """
    Возвращает данные текущего авторизованного пользователя (из токена).
    """
    return {'User': user}
