"""Pruebas de login, sesión firmada y límites."""

from __future__ import annotations

import time

import pytest
from auth import (
    DailyCounter,
    RateLimiter,
    check_password,
    derive_signing_key,
    make_session_token,
    verify_session_token,
)

PASSWORD = "gatito-de-prueba"


def test_password_compare_constante():
    assert check_password(PASSWORD, PASSWORD)
    assert not check_password(PASSWORD, "otra")
    assert not check_password(PASSWORD, "")


def test_session_token_firma_y_caducidad():
    key = derive_signing_key(PASSWORD)
    token = make_session_token(key, now=1000.0)
    assert verify_session_token(key, token, now=1001.0)
    assert not verify_session_token(key, token, now=1000.0 + 8 * 24 * 3600)
    assert not verify_session_token(key, "basura")
    assert not verify_session_token(key, None)
    otra_key = derive_signing_key("otra-clave")
    assert not verify_session_token(otra_key, token, now=1001.0)


def test_login_ok_emite_cookie(client):
    r = client.post("/api/login", json={"password": PASSWORD})
    assert r.status_code == 200
    assert "oficina_session" in r.cookies


def test_login_fallo_401(client):
    r = client.post("/api/login", json={"password": "mal"})
    assert r.status_code == 401


def test_login_limite_5_por_minuto(client):
    for _ in range(5):
        client.post("/api/login", json={"password": "mal"})
    r = client.post("/api/login", json={"password": "mal"})
    assert r.status_code == 429


def test_rutas_api_requieren_sesion(client):
    assert client.get("/api/equipo").status_code == 401
    r = client.post("/api/chat", json={"mensaje": "hola"})
    assert r.status_code == 401


def test_health_publico(client):
    r = client.get("/api/health")
    assert r.status_code == 200
    assert r.json()["ok"] is True


def test_sesion_valida_accede(client):
    client.post("/api/login", json={"password": PASSWORD})
    assert client.get("/api/equipo").status_code == 200


def test_rate_limiter_ventana():
    rl = RateLimiter(limit=2, window_seconds=60.0)
    assert rl.allow("ip", now=0.0)
    assert rl.allow("ip", now=1.0)
    assert not rl.allow("ip", now=2.0)
    assert rl.allow("ip", now=61.0)


def test_daily_counter():
    dc = DailyCounter(2)
    assert dc.try_consume(now=1_700_000_000.0)
    assert dc.try_consume(now=1_700_000_000.0)
    assert not dc.try_consume(now=1_700_000_000.0)
    assert dc.try_consume(now=1_700_086_400.0)  # otro día: se reinicia
