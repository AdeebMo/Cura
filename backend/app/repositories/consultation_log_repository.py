from __future__ import annotations

import json
from pathlib import Path
from threading import RLock
from typing import Any

from app.core.config import Settings, settings


class ConsultationLogRepository:
    def __init__(self, path: Path | None = None, repo_settings: Settings = settings) -> None:
        self._settings = repo_settings
        self._path = path or repo_settings.consultation_log_path
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = RLock()

    def append(self, payload: dict[str, Any]) -> None:
        if not self._settings.write_debug_snapshots:
            return
        line = json.dumps(payload, ensure_ascii=True)
        with self._lock:
            with self._path.open("a", encoding="utf-8") as handle:
                handle.write(f"{line}\n")
