from __future__ import annotations

from contextlib import contextmanager
from functools import lru_cache
from pathlib import Path
from typing import Iterator

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import Settings, settings
from app.db.base import Base


class DatabaseRuntime:
    def __init__(self, runtime_settings: Settings = settings) -> None:
        self._settings = runtime_settings
        self._engine = self._create_engine()
        self._session_factory = sessionmaker(
            bind=self._engine,
            autoflush=False,
            expire_on_commit=False,
            future=True,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def _create_engine(self) -> Engine:
        database_url = self._settings.resolved_database_url
        connect_args: dict[str, object] = {}

        if database_url.startswith("sqlite"):
            database_path = database_url.split("///", maxsplit=1)[-1]
            Path(database_path).parent.mkdir(parents=True, exist_ok=True)
            connect_args["check_same_thread"] = False

        return create_engine(
            database_url,
            echo=self._settings.database_echo,
            future=True,
            pool_pre_ping=True,
            connect_args=connect_args,
        )

    def initialize_schema(self) -> None:
        Base.metadata.create_all(self._engine)

    @contextmanager
    def session_scope(self) -> Iterator[Session]:
        session = self._session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


@lru_cache(maxsize=1)
def get_database_runtime() -> DatabaseRuntime:
    return DatabaseRuntime(settings)
