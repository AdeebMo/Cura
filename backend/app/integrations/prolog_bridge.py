from __future__ import annotations

import json
import subprocess
from typing import Any

from app.core.config import Settings, settings
from app.domain.models import DiagnosticBundle, DiagnosisResult, FollowUpQuestion, SafetyAlert


class PrologBridgeError(RuntimeError):
    """Raised when the Prolog bridge fails."""


class PrologBridge:
    def __init__(self, bridge_settings: Settings = settings) -> None:
        self._settings = bridge_settings

    def diagnose(self, request_payload: dict[str, Any]) -> DiagnosticBundle:
        process = subprocess.run(
            [self._settings.swipl_command, "-q", "-s", str(self._settings.prolog_entrypoint)],
            input=json.dumps(request_payload),
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )

        if process.returncode != 0:
            raise PrologBridgeError(process.stderr.strip() or "Prolog diagnosis failed")

        raw_output = process.stdout.strip()
        if not raw_output:
            raise PrologBridgeError("Prolog diagnosis returned no output")

        try:
            parsed = json.loads(raw_output)
        except json.JSONDecodeError as exc:
            raise PrologBridgeError(f"Could not decode Prolog output: {exc}") from exc

        diagnoses = [
            DiagnosisResult(
                condition=item["condition"],
                rule_strength=item["rule_strength"],
                matched_symptoms=item.get("matched_symptoms", []),
                missing_symptoms=item.get("missing_symptoms", []),
                conflicting_symptoms=item.get("conflicting_symptoms", []),
                explanation=item["explanation"],
            )
            for item in parsed.get("diagnoses", [])
        ]

        next_question = None
        if parsed.get("next_question"):
            question = parsed["next_question"]
            next_question = FollowUpQuestion(
                id=question["id"],
                prompt=question["prompt"],
                target_symptom=question["target_symptom"],
                rationale=question["rationale"],
            )

        red_flags = [
            SafetyAlert(
                id=item["id"],
                severity=item["severity"],
                message=item["message"],
                trigger=item["trigger"],
            )
            for item in parsed.get("red_flags", [])
        ]

        return DiagnosticBundle(
            diagnoses=diagnoses,
            next_question=next_question,
            red_flags=red_flags,
            explanation_trace=parsed.get("explanation_trace", []),
        )

