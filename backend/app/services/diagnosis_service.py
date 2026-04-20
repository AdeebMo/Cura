from __future__ import annotations

from typing import Any

from app.domain.models import DiagnosticBundle
from app.integrations.prolog_bridge import PrologBridge


class DiagnosisService:
    def __init__(self, prolog_bridge: PrologBridge) -> None:
        self._prolog_bridge = prolog_bridge

    def diagnose(self, request_payload: dict[str, Any]) -> DiagnosticBundle:
        return self._prolog_bridge.diagnose(request_payload)
