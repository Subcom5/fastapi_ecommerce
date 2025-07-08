from pydantic import BaseModel, Field


class CreateProduct(BaseModel):
    name: str = Field(..., description='Название продукта', examples=['Электродрель'])
    description: str = Field(..., description='Описание продукта', examples=['Сверхмощная дрель'])
    price: int  = Field(..., description='Цена продукта', examples=[1000])
    image_url: str = Field(..., description='Ссылка на изображение', examples=['https://example.com/image.jpg'])
    stock: int = Field(..., description='Остаток на складе', examples=[8])
    category: int = Field(..., description='ID категории', examples=[3])


class CreateCategory(BaseModel):
    name: str = Field(..., description='Название категории', examples=['Инструменты'])
    parent_id: int | None = Field(default=None ,description='ID родительской категории', examples=[33])
