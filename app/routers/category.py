from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session
from typing import Annotated
from sqlalchemy import insert, select, update
from slugify import slugify

from app.backend.db_depends import get_db
from app.schemas import CreateCategory
from app.models.category import Category


router = APIRouter(prefix='/categories', tags=['category'])


@router.get('/')
async def get_all_categories(
        db: Annotated[Session, Depends(get_db)]     # Получаем подключение к БД через Depends
):
    # Выполняем SELECT * FROM categories WHERE is_active = true
    # scalars() возвращает множество объектов (а не одно значение)
    categories = db.scalars(
        select(Category).where(Category.is_active == True)
    ).all()
    # Возвращаем список категорий (FastAPI преобразует в JSON)
    return categories


@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_category(
        db: Annotated[Session, Depends(get_db)],    # Получаем подключение к БД через Depends
        create_category: CreateCategory             # Данные запроса JSON автоматически валидируются через Pydantic
):
    # Вставка новой категории в таблицу categories с помощью SQLAlchemy insert
    db.execute(
        insert(Category).values(
            name=create_category.name,              # Название категории из тела запроса
            parent_id=create_category.parent_id,    # ID родительской категории (или None)
            slug=slugify(create_category.name)      # автоматическое создание "slug" (/categories/ruchnoy-instrument)
        )
    )
    # Завершаем транзакцию - коммитим изменения в БД
    db.commit()
    # Отправляем ответ клиенту - статус и подтверждение
    return {
        'status code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.put('/{category_slug}')
async def update_category(
        db: Annotated[Session, Depends(get_db)],    # Получаем подключение к БД через Depends
        category_slug: str,                         # Параметр пути - slug категории
        update_category: CreateCategory             # Данные запроса на обновление данных
):
    # Ищем категорию по slug и проверяем, что она активна
    category = db.scalar(select(Category).where(Category.slug == category_slug))
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    # Обновляем данные в базе данных
    db.execute(update(Category).where(Category.slug == category_slug).values(
        name=update_category.name,
        slug=slugify(update_category.name),
        parent_id=update_category.parent_id
    ))
    # Завершаем транзакцию - коммитим изменения в БД
    db.commit()
    # Отправляем ответ клиенту - статус и подтверждение
    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Category update is successful'
    }


@router.delete('/{category_slug}')
async def delete_category(
        db: Annotated[Session, Depends(get_db)],    # Получаем подключение к БД через Depends
        category_slug: str                          # Параметр пути - slug категории
):
    # Ищем категорию по slug и проверяем, что она активна
    category = db.scalar(
        select(Category).where(
            Category.slug == category_slug,
            Category.is_active == True
        )
    )
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no category found'
        )
    db.execute(
        update(Category).where(
            Category.slug == category_slug).values(is_active=False)
    )
    # Завершаем транзакцию - коммитим изменения в БД
    db.commit()
    # Отправляем ответ клиенту - статус и подтверждение
    return {
        'status code': status.HTTP_200_OK,
        'transaction': 'Category delete is successful'
    }
