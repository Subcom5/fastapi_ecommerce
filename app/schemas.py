from pydantic import BaseModel, Field, EmailStr


class CreateProduct(BaseModel):
    """
    Схема для создания нового продукта.
    """
    name: str = Field(..., description='Название продукта', examples=['Электродрель'])
    description: str = Field(..., description='Описание продукта', examples=['Сверхмощная дрель'])
    price: int  = Field(..., description='Цена продукта', examples=[1000])
    image_url: str = Field(..., description='Ссылка на изображение', examples=['https://example.com/image.jpg'])
    stock: int = Field(..., description='Остаток на складе', examples=[8])
    category: int = Field(..., description='ID категории', examples=[3])


class CreateCategory(BaseModel):
    """
    Схема для создания новой категории продуктов.
    """
    name: str = Field(..., description='Название категории', examples=['Инструменты'])
    parent_id: int | None = Field(default=None ,description='ID родительской категории', examples=[33])


class CreateUser(BaseModel):
    """
    Схема создания нового пользователя.
    """
    first_name: str = Field(..., description='Имя пользователя', examples=['Ivan'])
    last_name: str = Field(..., description='Фамилия пользователя', examples=['Ivanov'])
    username: str = Field(..., description='Логин пользователя', examples=['MisterX'])
    email: EmailStr = Field(..., description='Email', examples=['mail@example.com'])
    password: str = Field(..., description='Пароль', examples=['12345'])
