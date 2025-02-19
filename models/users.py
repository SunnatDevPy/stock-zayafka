from sqlalchemy import BigInteger, Text
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
    chat_id: Mapped[int] = mapped_column(BigInteger)
    name: Mapped[str]
    status: Mapped[bool]


class TextInSend(BaseModel):
    text: Mapped[str] = mapped_column(Text, nullable=True)
    link: Mapped[str]
