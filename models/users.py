from sqlalchemy import BigInteger, Text, JSON, ForeignKey
from sqlalchemy import String
from sqlalchemy.orm import mapped_column, Mapped

from models.database import BaseModel


class BotUser(BaseModel):
    first_name: Mapped[str] = mapped_column(String(255), nullable=True)
    last_name: Mapped[str] = mapped_column(String(255), nullable=True)
    username: Mapped[str] = mapped_column(String(255), nullable=True)
    is_premium: Mapped[bool] = mapped_column(nullable=True)

    def __str__(self):
        return super().__str__() + f" - {self.username}"


class Channels(BaseModel):
    chat_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(nullable=True)
    text: Mapped[str] = mapped_column(nullable=True)
    photo: Mapped[str] = mapped_column(nullable=True)
    video: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[bool] = mapped_column(nullable=True)
    link: Mapped[str] = mapped_column(nullable=True)


class Buttons(BaseModel):
    channel_id: Mapped[int] = mapped_column(BigInteger, ForeignKey(Channels.id, ondelete="CASCADE"))
    link: Mapped[str] = mapped_column(nullable=True)
    name: Mapped[str] = mapped_column(nullable=True)


class TextZayafka(BaseModel):
    photo: Mapped[str]
    name: Mapped[str]
    status: Mapped[bool]
