from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from starlette import status
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.user import User
from app.routers.auth import get_current_user


# Создание маршрутизатора для работы с правами (permissions)
router = APIRouter(prefix='/permission', tags=['permission'])


@router.patch('/')
async def supplier_permission(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: int
):
    """
        Изменяет статус пользователя: становится продавцом (supplier) или больше не является им.
        Только администратор может вызывать этот метод.

        Если пользователь уже продавец — статус отменяется и он становится клиентом.
        Если не был продавцом — становится им, клиентский статус снимается.
        """
    # Проверка: является ли текущий пользователь админом
    if get_user.get('is_admin'):
        # Пытаемся найти пользователя по ID
        user = await db.scalar(select(User).where(User.id == user_id))

        # Если пользователь не найден или деактивирован — ошибка 404
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        # Если пользователь уже является поставщиком — снимаем статус
        if user.is_supplier:
            await db.execute(
                update(User).where(User.id == user_id).values(
                    is_supplier=False, is_customer=True
                ))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is no longer supplier'
            }

        # Если пользователь не был поставщиком — назначаем поставщиком
        else:
            await db.execute(
                update(User).where(User.id == user_id).values(
                    is_supplier=True,
                    is_customer=False
                ))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is now supplier'
            }

    # Если текущий пользователь не админ — отказ в доступе
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You dont have admin permission'
        )


@router.delete('/delete')
async def delete_user(
        db: Annotated[AsyncSession, Depends(get_db)],
        get_user: Annotated[dict, Depends(get_current_user)],
        user_id: int
):
    """
    Деактивирует пользователя (is_active = False) по его ID.
    Только администратор может выполнить это действие.

    - Если пользователь не найден — ошибка 404.
    - Если пользователь является админом — удаление запрещено.
    - Если пользователь уже не активен — возвращается соответствующее сообщение.
    """
    # Проверяем, имеет ли текущий пользователь права администратора
    if get_user.get('is_admin'):
        # Получаем пользователя из базы по ID
        user = await db.scalar(select(User).where(User.id == user_id))

        # Если пользователь не найден — ошибка 404
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='User not found'
            )

        # Защита: нельзя удалить администратора
        if user.is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't admin user"
            )

        # Если пользователь активен — деактивируем (мягкое удаление)
        if user.is_active:
            await db.execute(update(User).where(User.id == user_id).values(is_active=False))
            await db.commit()
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User is deleted'
            }
        # Если пользователь уже деактивирован — просто сообщаем об этом
        else:
            return {
                'status_code': status.HTTP_200_OK,
                'detail': 'User has already been deleted'
            }
    # Если текущий пользователь не админ — отказ в доступе
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You dont have admin permission'
        )
