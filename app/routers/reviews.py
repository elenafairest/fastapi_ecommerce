from typing import Annotated

from app.schemas import CreateReview
from fastapi import APIRouter, Depends, status, HTTPException

from sqlalchemy import insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.backend.db_depends import get_db
from app.models.review import Review
from app.models.products import Product
from app.models.user import User

from app.routers.auth import get_current_user

from datetime import date

router = APIRouter(prefix='/reviews', tags=['reviews'])


@router.get('/')
async def all_reviews(db: Annotated[AsyncSession, Depends(get_db)]):
    reviews = await db.scalars(
        select(Review).where(Review.is_active == True))
    all_reviews = reviews.all()
    if not all_reviews:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='There are no reviews'
        )
    return all_reviews


@router.get('/{product_slug}')
async def products_reviews(db: Annotated[AsyncSession, Depends(get_db)], product_slug: str):
    product = await db.scalar(select(Product).where(Product.slug == product_slug))
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Product not found'
        )
    reviews_product = await db.scalars(
        select(Review).where(Review.product_id == product.id, Review.is_active == True))
    return reviews_product.all()


@router.post('/')
async def create_product(db: Annotated[AsyncSession, Depends(get_db)], create_review: CreateReview,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_customer'):
        product = await db.scalar(select(Product).where(Product.id == create_review.product))
        if product is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no product found'
            )
        user = await db.scalar(select(User).where(User.id == create_review.user))
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no user found'
            )
        await db.execute(insert(Review).values(user_id=create_review.user,
                                               product_id=create_review.product,
                                               comment=create_review.comment,
                                               comment_date=date.today(),
                                               grade=create_review.grade))
        reviews_product = await db.scalars(
            select(Review).where(Review.product_id == product.id, Review.is_active == True))
        grades = [review.grade for review in reviews_product.all()]
        rating = sum(grades) / len(grades)
        product.rating = rating
        await db.commit()
        return {
            'status_code': status.HTTP_201_CREATED,
            'transaction': 'Successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be customer user for this'
        )


@router.delete('/')
async def delete_reviews(db: Annotated[AsyncSession, Depends(get_db)], review_id: int,
                         get_user: Annotated[dict, Depends(get_current_user)]):
    if get_user.get('is_admin'):
        review = await db.scalar(select(Review).where(Review.id == review_id))
        if review is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail='There is no review found'
            )
        review.is_active = False
        await db.commit()
        return {
            'status_code': status.HTTP_200_OK,
            'transaction': 'Review delete is successful'
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='You must be admin user for this'
        )
