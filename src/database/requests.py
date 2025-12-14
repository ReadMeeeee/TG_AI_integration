from datetime import datetime, timezone

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database import ChatState


def _ts():
    """Текущая дата и время в UTC в ISO-формате."""
    return datetime.now(timezone.utc).isoformat()


async def get_state(session: AsyncSession, tg_user_id: int):
    """
    Получить состояние чата пользователя по tg_user_id.
    Возвращает ChatState или None, если записи нет
    """
    stmt = select(ChatState).where(ChatState.tg_user_id == tg_user_id)
    res = await session.execute(stmt)
    return res.scalar_one_or_none()


async def create_or_reset_state(session: AsyncSession, tg_user_id: int):
    """
    Создать запись пользователя, если её нет, или сбросить существующую.

    Использовать в обработчике /start:
    - гарантирует наличие записи в БД
    - очищает messages и summary
    - обновляет updated_at (через ORM update!)
    """
    state = await get_state(session, tg_user_id)

    if state is None:
        state = ChatState(tg_user_id=tg_user_id, messages=[], summary="")
        session.add(state)
    else:
        state.messages = []
        state.summary = ""

    await session.commit()
    await session.refresh(state)
    return state


async def update_summary(session: AsyncSession, tg_user_id: int, summary: str):
    """
    Обновить summary для существующего пользователя
    """
    state = await get_state(session, tg_user_id)
    if state is None:
        raise RuntimeError("ChatState not initialized. Call /start first.")

    state.summary = summary or ""
    await session.commit()
    await session.refresh(state)
    return state


async def add_pair(session: AsyncSession, tg_user_id: int, user_text: str, assistant_text: str, keep_last: int = 20):
    """
    Добавить пару сообщений (user + assistant) в историю.

    - messages хранится в JSONB
    - автоматически обрезается до keep_last (по умолчанию 20 сообщений = 10 пар)
    """
    state = await get_state(session, tg_user_id)
    if state is None:
        raise RuntimeError("ChatState not initialized. Call /start first.")

    state.messages = (state.messages or []) + [
        {"role": "user", "content": user_text, "ts": _ts()},
        {"role": "assistant", "content": assistant_text, "ts": _ts()},
    ]

    if keep_last and len(state.messages) > keep_last:
        state.messages = state.messages[-keep_last:]

    await session.commit()
    await session.refresh(state)
    return state


async def delete_state(session: AsyncSession, tg_user_id: int):
    """
    Полностью удалить состояние чата пользователя из БД.
    Возвращает True, если запись была удалена.
    """
    stmt = (
        delete(ChatState)
        .where(ChatState.tg_user_id == tg_user_id)
        .returning(ChatState.tg_user_id)
    )
    res = await session.execute(stmt)
    deleted_id = res.scalar_one_or_none()
    await session.commit()
    return deleted_id is not None
