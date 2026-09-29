"""Retained upstream proxy behavior, updated for stateless configuration."""

import pytest
from app.transcript_service import get_proxy_url


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ("YT_PROXY", "HTTPS_PROXY", "HTTP_PROXY", "SOCKS5_PROXY"):
        monkeypatch.delenv(key, raising=False)


def test_yt_proxy_priority(monkeypatch):
    monkeypatch.setenv("YT_PROXY", "http://yt-proxy:8080")
    monkeypatch.setenv("HTTP_PROXY", "http://http-proxy:8080")
    assert get_proxy_url() == "http://yt-proxy:8080"


def test_http_proxy_fallback(monkeypatch):
    monkeypatch.setenv("HTTP_PROXY", "http://http-proxy:8080")
    assert get_proxy_url() == "http://http-proxy:8080"


def test_socks5_fallback(monkeypatch):
    monkeypatch.setenv("SOCKS5_PROXY", "socks5://socks5-proxy:9090")
    assert get_proxy_url() == "socks5://socks5-proxy:9090"


def test_no_proxy():
    assert get_proxy_url() is None
