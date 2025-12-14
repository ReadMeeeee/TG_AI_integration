from datetime import datetime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import BigInteger, Text, DateTime, func, text


class Base(DeclarativeBase): pass


class ChatState(Base):
    """
    Таблица данных пользователя:
    - tg_user_id: ID, закрепленный за пользователем ТГ
    - messages: массив последних единиц вида вопрос-ответ
    - summary: выжимка из всего диалога с пользователем
    - updated_at: дата и время последнего обновления (создания чата)
    """

    __tablename__ = "user_data"

    tg_user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)

    messages: Mapped[list] = mapped_column(
        JSONB,
        nullable=False,
        server_default=text("'[]'::jsonb"),
        default=list,
    )

    summary: Mapped[str] = mapped_column(
        Text,
        nullable=False,
        server_default="",
        default="",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
