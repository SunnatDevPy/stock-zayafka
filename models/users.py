from sqlalchemy import BigInteger, Text, JSON
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from models.database import BaseModel


class BotUser(BaseModel):
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)

    def __str__(self):
        return super().__str__() + f" - {self.username}"


class Channels(BaseModel):
    chat_id: Mapped[int] = mapped_column(BigInteger)  # ID чата (канала)
    name: Mapped[str]  # Название канала
    text: Mapped[str] = mapped_column(nullable=True)  # Текст сообщения
    photo: Mapped[str] = mapped_column(nullable=True)  # Фото (file_id)
    video: Mapped[str] = mapped_column(nullable=True)  # Видео (file_id)
    document: Mapped[str] = mapped_column(nullable=True)  # Документ (file_id)
    status: Mapped[bool]  # Статус канала
    link: Mapped[str] = mapped_column(nullable=True)  # Ссылка
    buttons: Mapped[dict] = mapped_column(JSON, nullable=True)
