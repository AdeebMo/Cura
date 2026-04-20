from __future__ import annotations

from threading import RLock

from app.domain.models import UserSession


class SessionNotFoundError(KeyError):
    """Raised when a session lookup fails."""


class InMemorySessionStore:
    def __init__(self) -> None:
        self._sessions: dict[str, UserSession] = {}
        self._lock = RLock()

    def save(self, session: UserSession) -> UserSession:
        with self._lock:
            self._sessions[session.session_id] = session
            return session

    def get(self, session_id: str) -> UserSession:
        with self._lock:
            try:
                return self._sessions[session_id]
            except KeyError as exc:
                raise SessionNotFoundError(session_id) from exc

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._sessions.pop(session_id, None)

