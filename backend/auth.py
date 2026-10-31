"""Autenticación de la oficina: contraseña única y cookie de sesión firmada.

La clave de firma de la cookie se deriva de APP_PASSWORD con HMAC-SHA256, así
que no hace falta ninguna variable secreta adicional. La contraseña se compara
con `hmac.compare_digest` (tiempo constante).

Los contadores de límite viven EN MEMORIA: se reinician cuando el proceso
reinicia (p. ej. cuando Render despierta/reinicia el servicio en el plan gratis).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from collections import deque
from dataclasses import dataclass, field

SESSION_COOKIE = "oficina_session"
SESSION_TTL_SECONDS = 7 * 24 * 3600  # 7 días
_SIGNING_CONTEXT = b"oficina-kawaii-3d/session/v1"

LOGIN_LIMIT = 5  # intentos de login por minuto por IP
LOGIN_WINDOW = 60.0
AI_LIMIT = 15  # peticiones a la IA por minuto por sesión
AI_WINDOW = 60.0


def derive_signing_key(app_password: str) -> bytes:
    """Deriva la clave de firma de la cookie a partir de APP_PASSWORD (HMAC)."""
    return hmac.new(app_password.encode("utf-8"), _SIGNING_CONTEXT, hashlib.sha256).digest()


def _b64e(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64d(data: str) -> bytes:
    return base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))


def make_session_token(signing_key: bytes, now: float | None = None) -> str:
    """Crea un token de sesión firmado: payload_b64.firma_b64."""
    now = time.time() if now is None else now
    payload = _b64e(json.dumps({"exp": now + SESSION_TTL_SECONDS}, separators=(",", ":")).encode())
    sig = hmac.new(signing_key, payload.encode("ascii"), hashlib.sha256).digest()
    return f"{payload}.{_b64e(sig)}"


def verify_session_token(signing_key: bytes, token: str | None, now: float | None = None) -> bool:
    """Verifica firma y caducidad del token. Nunca lanza por token malformado."""
    if not token or "." not in token:
        return False
    payload, _, sig_b64 = token.rpartition(".")
    if not payload or not sig_b64:
        return False
    try:
        expected = hmac.new(signing_key, payload.encode("ascii"), hashlib.sha256).digest()
        given = _b64d(sig_b64)
    except Exception:
        return False
    if not hmac.compare_digest(expected, given):
        return False
    try:
        data = json.loads(_b64d(payload))
        exp = float(data["exp"])
    except Exception:
        return False
    now = time.time() if now is None else now
    return exp >= now


def check_password(app_password: str, candidate: str) -> bool:
    """Comparación de contraseña en tiempo constante."""
    return hmac.compare_digest(app_password.encode("utf-8"), candidate.encode("utf-8"))


@dataclass
class RateLimiter:
    """Limitador de ventana deslizante en memoria (se reinicia con el proceso)."""

    limit: int
    window_seconds: float
    _hits: dict[str, deque[float]] = field(default_factory=dict)

    def allow(self, key: str, now: float | None = None) -> bool:
        """Registra un intento para `key` y devuelve True si está dentro del límite."""
        now = time.time() if now is None else now
        bucket = self._hits.setdefault(key, deque())
        while bucket and now - bucket[0] >= self.window_seconds:
            bucket.popleft()
        if len(bucket) >= self.limit:
            return False
        bucket.append(now)
        return True


class DailyCounter:
    """Contador diario global de llamadas a la IA (en memoria, se reinicia)."""

    def __init__(self, max_per_day: int) -> None:
        self.max_per_day = max_per_day
        self._day = ""
        self._count = 0

    def try_consume(self, now: float | None = None) -> bool:
        """Consume una unidad del tope diario si queda; devuelve si se pudo."""
        import datetime as _dt

        now = time.time() if now is None else now
        day = _dt.datetime.fromtimestamp(now, _dt.timezone.utc).date().isoformat()
        if day != self._day:
            self._day = day
            self._count = 0
        if self._count >= self.max_per_day:
            return False
        self._count += 1
        return True


login_limiter = RateLimiter(limit=LOGIN_LIMIT, window_seconds=LOGIN_WINDOW)
ai_limiter = RateLimiter(limit=AI_LIMIT, window_seconds=AI_WINDOW)
