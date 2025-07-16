from sqlalchemy import Integer, String, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime

from app.backend.db import Base



class Reviews(Base):
    __tablename__ = 'reviews'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey('products.id'), nullable=False)
    comment: Mapped[str] = mapped_column(String, nullable=True)
    comment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=True)
    grade: Mapped[int] = mapped_column(Integer, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=True)

    user: Mapped['User'] = relationship(back_populates='reviews')
    product: Mapped['Product'] = relationship(back_populates='reviews')
