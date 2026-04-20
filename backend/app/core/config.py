from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    project_root: Path = Path(__file__).resolve().parents[3]
    backend_root: Path = Path(__file__).resolve().parents[2]
    sbcl_command: str = "sbcl"
    swipl_command: str = "swipl"
    frontend_origin: str = "http://localhost:5173"

    @property
    def lisp_entrypoint(self) -> Path:
        return self.project_root / "lisp" / "src" / "main.lisp"

    @property
    def prolog_entrypoint(self) -> Path:
        return self.project_root / "prolog" / "src" / "main.pl"

    @property
    def consultation_log_path(self) -> Path:
        return self.backend_root / "data" / "consultations.jsonl"


settings = Settings()

