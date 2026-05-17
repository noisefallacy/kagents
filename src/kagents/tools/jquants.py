"""Minimal J-Quants V2 tools."""

from __future__ import annotations

from datetime import date
from typing import Any

import requests

from kagents.config import settings


JQUANTS_BASE_URL = "https://api.jquants.com/v2"


def normalize_security_code(code: str) -> str:
    digits = "".join(ch for ch in code if ch.isdigit())
    if len(digits) == 4:
        return digits + "0"
    return digits or code.strip()


def get_jquants_daily_quote(code: str, target_date: str | None = None) -> dict[str, Any]:
    """
    Fetch a daily quote from J-Quants API V2 for a single security code.

    Args:
        code: Security code. 4-digit codes are normalized to 5 digits by appending 0.
        target_date: Date in YYYY-MM-DD format. Defaults to today when omitted.
    """

    if not settings.jquants_api_key:
        return {
            "status": "error",
            "message": "JQUANTS_API_KEY is not configured.",
            "result": None,
        }

    normalized_code = normalize_security_code(code)
    quote_date = target_date or str(date.today())

    response = requests.get(
        f"{JQUANTS_BASE_URL}/equities/bars/daily",
        params={"code": normalized_code, "date": quote_date},
        headers={"x-api-key": settings.jquants_api_key},
        timeout=30,
    )

    if response.status_code >= 400:
        return {
            "status": "error",
            "message": f"J-Quants API error: {response.status_code} {response.text}",
            "result": None,
        }

    payload = response.json()
    quotes = payload.get("daily_quotes")
    if quotes is None:
        quotes = payload.get("data", [])
    first_quote = quotes[0] if quotes else None

    return {
        "status": "success",
        "code": normalized_code,
        "date": quote_date,
        "result": first_quote,
        "raw_count": len(quotes),
    }
