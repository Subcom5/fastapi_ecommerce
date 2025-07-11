from sqlalchemy import Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.backend.db import Base
from app.models.products import Product


class Category(Base):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer ,primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)
    parent_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), nullable=True)

    products: Mapped[list['Product']] = relationship(
        back_populates='category'
    )

