from __future__ import annotations

import subprocess

from app.core.config import Settings, settings
from app.domain.models import MatchedPhrase, NormalizedInput
from app.integrations.sexp import SExpressionParseError, parse_sexp, plist_to_dict


class LispBridgeError(RuntimeError):
    """Raised when the Lisp bridge fails."""


class LispBridge:
    def __init__(self, bridge_settings: Settings = settings) -> None:
        self._settings = bridge_settings

    @staticmethod
    def _list_field(value: object) -> list[object]:
        if isinstance(value, list):
            return value
        if isinstance(value, str) and value.upper() == "NIL":
            return []
        return []

    def normalize(self, text: str) -> NormalizedInput:
        process = subprocess.run(
            [self._settings.sbcl_command, "--script", str(self._settings.lisp_entrypoint)],
            input=text,
            capture_output=True,
            text=True,
            check=False,
            timeout=5,
        )

        if process.returncode != 0:
            raise LispBridgeError(process.stderr.strip() or "Lisp normalization failed")

        raw_output = process.stdout.strip()
        if not raw_output:
            raise LispBridgeError("Lisp normalization returned no output")

        try:
            parsed = plist_to_dict(parse_sexp(raw_output))
        except SExpressionParseError as exc:
            raise LispBridgeError(f"Could not parse Lisp output: {exc}") from exc

        canonical_symptoms = [
            value
            for value in self._list_field(parsed.get("canonical-symptoms", []))
            if isinstance(value, str)
        ]
        matched_phrases = [
            MatchedPhrase(source=pair[0], canonical=pair[1])
            for pair in self._list_field(parsed.get("matched-phrases", []))
            if isinstance(pair, list) and len(pair) == 2
        ]
        unknown_terms = [
            value for value in self._list_field(parsed.get("unknown-terms", [])) if isinstance(value, str)
        ]

        return NormalizedInput(
            canonical_symptoms=canonical_symptoms,
            matched_phrases=matched_phrases,
            unknown_terms=unknown_terms,
        )
