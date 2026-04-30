from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


def _bool_env(name: str, default: bool) -> bool:
    raw_value = os.getenv(name)
    if raw_value is None:
        return default
    return raw_value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[3]
    backend_root: Path = Path(__file__).resolve().parents[2]
    sbcl_command: str = "sbcl"
    swipl_command: str = "swipl"
    frontend_origin: str = os.getenv("CURA_FRONTEND_ORIGIN", "http://localhost:5173")
    database_url: str | None = os.getenv("CURA_DATABASE_URL")
    database_echo: bool = _bool_env("CURA_DATABASE_ECHO", False)
    auto_initialize_database: bool = _bool_env("CURA_AUTO_INITIALIZE_DATABASE", True)
    validate_paradigms_on_startup: bool = _bool_env("CURA_VALIDATE_PARADIGMS_ON_STARTUP", True)

    @property
    def lisp_entrypoint(self) -> Path:
        return self.project_root / "lisp" / "src" / "main.lisp"

    @property
    def prolog_entrypoint(self) -> Path:
        return self.project_root / "prolog" / "src" / "main.pl"

    @property
    def resolved_database_url(self) -> str:
        if self.database_url:
            return self.database_url
        return f"sqlite+pysqlite:///{(self.backend_root / 'cura.db').as_posix()}"


settings = Settings()
