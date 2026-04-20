from __future__ import annotations

from sqlalchemy.orm import Session

from app.domain.models import NormalizedInput
from app.integrations.lisp_bridge import LispBridge
from app.repositories.symptom_catalog_repository import SymptomCatalogRepository


class NormalizationCatalogError(ValueError):
    """Raised when Lisp emits symptom keys outside the database catalog."""


class NormalizationService:
    def __init__(
        self,
        lisp_bridge: LispBridge,
        symptom_catalog_repository: SymptomCatalogRepository,
    ) -> None:
        self._lisp_bridge = lisp_bridge
        self._symptom_catalog_repository = symptom_catalog_repository

    def normalize(self, db_session: Session, text: str) -> NormalizedInput:
        normalized = self._lisp_bridge.normalize(text)
        known_canonical_keys = self._symptom_catalog_repository.canonical_keys(db_session)
        missing_keys = sorted(set(normalized.canonical_symptoms) - known_canonical_keys)
        if missing_keys:
            raise NormalizationCatalogError(
                "Lisp emitted symptom keys that are missing from the symptom catalog: "
                + ", ".join(missing_keys)
            )
        return normalized

    def canonical_inventory(self) -> set[str]:
        return set(self._lisp_bridge.canonical_inventory())
