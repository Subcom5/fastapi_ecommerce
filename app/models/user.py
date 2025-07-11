from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Integer, String, Boolean

from app.backend.db import Base


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String, nullable=True)
    last_name: Mapped[str] = mapped_column(String, nullable=True)
    username: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    hashed_password: Mapped[str] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_supplier: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
    is_customer: Mapped[bool] = mapped_column(Boolean, nullable=True, default=True)

