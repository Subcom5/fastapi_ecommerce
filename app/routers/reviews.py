from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Annotated
from sqlalchemy import insert, select, update, func

from app.backend.db_depends import get_db
from app.models.products import Product
from app.models.reviews import Reviews
from app.schemas import CreateReview
from app.routers.auth import get_current_user


router = APIRouter(prefix='/review', tags=['reviews'])


@router.get(
    '/',
    description="Метод получения всех отзывов о товарах. Разрешен доступ всем."
)
async def all_reviews(
        db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(select(Reviews).where(Reviews.is_active.is_(True)))
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Reviews not found'
        )
    return reviews.all()



@router.get(
    '/{product_id}',
    description='Метод получения отзывов об определенном товаре. Разрешен доступ всем.'
)
async def product_reviews(
        db: Annotated[AsyncSession, Depends(get_db)],
        product_id: int
):
    reviews = await db.scalars(select(Reviews).where(
        Reviews.is_active.is_(True),
        Reviews.product_id == product_id
    ))
    if not reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews for the product'
        )
    return reviews.all()


@router.post(
    '/',
    description='Метод добавления отзыва об определенном товаре. Разрешен доступ только пользователям.'
)
async def add_review(
        db: Annotated[AsyncSession, Depends(get_db)],
        create_review: CreateReview,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    if not get_user.get('is_customer'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )

    product = await db.scalar(select(Product).where(
        Product.is_active.is_(True),
        Product.id == create_review.product_id
    ))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no product found'
        )
    await db.execute(
        insert(Reviews).values(
            user_id=get_user['id'],
            product_id=create_review.product_id,
            comment=create_review.comment,
            grade=create_review.grade
        )
    )
    avg_rating = await db.scalar(select(func.avg(Reviews.grade)).where(
        Reviews.product_id == create_review.product_id,
            Reviews.is_active.is_(True)
        )
    )

    await db.execute(
        update(Product)
        .where(Product.id == create_review.product_id)
        .values(rating=round(avg_rating, 2) if avg_rating else None)
    )

    await db.commit()
    return {
        'status_code': status.HTTP_201_CREATED,
        'transaction': 'Successful'
    }


@router.delete(
    '/{review_id}',
    description='Метод удаления отзыва. Доступ разрешен только администратору.'
)
async def delete_review(
        db: Annotated[AsyncSession, Depends(get_db)],
        review_id: int,
        get_user: Annotated[dict, Depends(get_current_user)]
):
    if not get_user.get('is_admin'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You have not enough permission for this action'
        )
    review = await db.scalar(select(Reviews).where(
        Reviews.is_active.is_(True),
            Reviews.id == review_id
        )
    )
    if review is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There is no review found'
        )
    else:
        review.is_active = False
        await db.commit()

    return {
        'status_code': status.HTTP_200_OK,
        'transaction': 'Delete review'
    }
