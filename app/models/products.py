from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Float, Boolean, ForeignKey

from app.backend.db import Base


class Product(Base):
    __tablename__ = 'products'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, nullable=True)
    slug: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=True)
    description: Mapped[str] = mapped_column(String, nullable=True)
    price: Mapped[int] = mapped_column(Integer, nullable=True)
    image_url: Mapped[str] = mapped_column(String, nullable=True)
    stock: Mapped[int] = mapped_column(Integer, nullable=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'))
    rating: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    category: Mapped['Category'] = relationship(
        uselist=False,
        back_populates='products'
    )
