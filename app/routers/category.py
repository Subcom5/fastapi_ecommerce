from fastapi import APIRouter, Depends, status, HTTPException
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CreateCategory
from app.models.category import Category
from app.routers.auth import get_current_user


router = APIRouter(prefix='/categories', tags=['category'])


@router.get('/')
async def get_all_categories(
        db: Annotated[AsyncSession, Depends(get_db)]     # Получаем подключение к БД через Depends
):
    # Выполняем SELECT * FROM categories WHERE is_active = true
    # scalars() возвращает множество объектов (а не одно значение)
    categories = await db.scalars(
        select(Category).where(Category.is_active == True)
    )
    # Возвращаем список категорий (FastAPI преобразует в JSON)
    return categories.all()


@router.post('/')
async def create_category(
        db: Annotated[AsyncSession, Depends(get_db)],
        create_category: CreateCategory,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    if get_user.get('is_admin'):
        await db.execute(insert(Category).values(
            name=create_category.name,
            parent_id=create_category.parent_id,
            slug=slugify(create_category.name)
        ))
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )


@router.put('/')
async def update_category(
        db: Annotated[AsyncSession, Depends(get_db)],
        category_id: int,
        update_category: CreateCategory,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is not category found'
            )

        category.name = update_category.name
        category.slug = slugify(update_category.name)
        category.parent_id = update_category.parent_id

        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'detail': 'Category update is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )



@router.delete('/')
async def delete_category(
        db: Annotated[AsyncSession, Depends(get_db)],
        category_id: int,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    if get_user.get('is_admin'):
        category = await db.scalar(select(Category).where(Category.id == category_id))
        if category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no category found'
            )
        category.is_active = False
        await db.commit()
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
