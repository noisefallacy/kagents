"""Direct, guarded LSEG data tools."""

from __future__ import annotations

from contextlib import contextmanager
from datetime import date, timedelta
from typing import Any, Iterator

import pandas as pd

from kagents.config import settings
from kagents.tools.charting import create_chart_png


ALLOWED_FX_PAIRS = {
    "USDJPY": "JPY=",
    "EURJPY": "EURJPY=",
    "GBPJPY": "GBPJPY=",
    "AUDJPY": "AUDJPY=",
    "EURUSD": "EUR=",
    "GBPUSD": "GBP=",
}
ALLOWED_INTERVALS = {"daily", "weekly", "monthly"}
DEFAULT_HISTORY_DAYS = 90
MAX_HISTORY_DAYS = 3700
MAX_ROWS = 5000


def _normalize_pair(pair: str) -> str:
    normalized = pair.upper().replace("/", "").replace("-", "").strip()
    if normalized not in ALLOWED_FX_PAIRS:
        raise ValueError(
            f"Unsupported FX pair: {pair}. Allowed pairs: {sorted(ALLOWED_FX_PAIRS)}"
        )
    return normalized


def _normalize_interval(interval: str) -> str:
    normalized = interval.strip().lower()
    if normalized not in ALLOWED_INTERVALS:
        raise ValueError(
            f"Unsupported interval: {interval}. Allowed intervals: {sorted(ALLOWED_INTERVALS)}"
        )
    return normalized


def _parse_date(value: str | None, fallback: date) -> date:
    if not value:
        return fallback
    return date.fromisoformat(value)


def _validated_dates(start_date: str | None, end_date: str | None) -> tuple[str, str]:
    end = _parse_date(end_date, date.today())
    start = _parse_date(start_date, end - timedelta(days=DEFAULT_HISTORY_DAYS))
    if start > end:
        raise ValueError("start_date must be on or before end_date")
    if (end - start).days > MAX_HISTORY_DAYS:
        raise ValueError(f"Date range is too large. Maximum is {MAX_HISTORY_DAYS} days.")
    return start.isoformat(), end.isoformat()


def _credentials_configured() -> bool:
    if settings.lseg_session_method.lower() == "desktop":
        return True
    return bool(settings.lseg_app_key and settings.lseg_username and settings.lseg_password)


@contextmanager
def _open_lseg_session() -> Iterator[Any]:
    import lseg.data as ld

    method = settings.lseg_session_method.lower()
    if method == "desktop":
        session = ld.open_session()
    elif method == "remote":
        if not _credentials_configured():
            raise RuntimeError(
                "LSEG remote credentials are not configured. Set LSEG_APP_KEY, "
                "LSEG_USERNAME, and LSEG_PASSWORD in .env."
            )
        session = ld.session.platform.Definition(
            app_key=settings.lseg_app_key,
            grant=ld.session.platform.GrantPassword(
                username=settings.lseg_username,
                password=settings.lseg_password,
            ),
            signon_control=True,
        ).get_session()
        session.open()
    else:
        raise RuntimeError("LSEG_SESSION_METHOD must be 'remote' or 'desktop'.")

    try:
        ld.session.set_default(session)
        yield ld
    finally:
        try:
            session.close()
        except Exception:
            pass


def _history_to_series(df: pd.DataFrame, ric: str, pair: str) -> list[dict[str, Any]]:
    if df is None or df.empty:
        return []

    frame = df.copy()
    if not isinstance(frame.index, pd.DatetimeIndex):
        frame.index = pd.to_datetime(frame.index)

    if isinstance(frame.columns, pd.MultiIndex):
        if ric in frame.columns.get_level_values(0):
            series = frame[ric].iloc[:, 0]
        else:
            series = frame.iloc[:, 0]
    else:
        series = frame[ric] if ric in frame.columns else frame.iloc[:, 0]

    output = []
    for timestamp, value in series.dropna().items():
        output.append(
            {
                "date": pd.Timestamp(timestamp).date().isoformat(),
                "pair": pair,
                "ric": ric,
                "value": float(value),
            }
        )
    return output


def get_lseg_fx_history(
    pair: str = "USDJPY",
    start_date: str | None = None,
    end_date: str | None = None,
    interval: str = "daily",
) -> dict[str, Any]:
    """
    Fetch a guarded FX history series directly from LSEG.

    Args:
        pair: Allowed FX pair, such as USDJPY.
        start_date: Optional ISO date. Defaults to 90 days before end_date.
        end_date: Optional ISO date. Defaults to today.
        interval: daily, weekly, or monthly.
    """

    try:
        normalized_pair = _normalize_pair(pair)
        normalized_interval = _normalize_interval(interval)
        start, end = _validated_dates(start_date, end_date)
    except ValueError as exc:
        return {
            "status": "error",
            "message": str(exc),
            "results": [],
        }

    ric = ALLOWED_FX_PAIRS[normalized_pair]
    if not _credentials_configured():
        return {
            "status": "error",
            "message": (
                "LSEG credentials are not configured. Set LSEG_APP_KEY, "
                "LSEG_USERNAME, and LSEG_PASSWORD in .env, or use desktop session mode."
            ),
            "results": [],
            "pair": normalized_pair,
            "ric": ric,
        }

    try:
        with _open_lseg_session() as ld:
            df = ld.get_history(
                universe=[ric],
                fields=["MID_PRICE"],
                start=start,
                end=end,
                interval=normalized_interval,
            )
    except Exception as exc:
        return {
            "status": "error",
            "message": f"LSEG history request failed: {exc}",
            "results": [],
            "pair": normalized_pair,
            "ric": ric,
        }

    results = _history_to_series(df, ric=ric, pair=normalized_pair)
    if len(results) > MAX_ROWS:
        results = results[-MAX_ROWS:]

    return {
        "status": "success",
        "pair": normalized_pair,
        "ric": ric,
        "start_date": start,
        "end_date": end,
        "interval": normalized_interval,
        "results": results,
        "row_count": len(results),
    }


def plot_lseg_fx_history(
    pair: str = "USDJPY",
    start_date: str | None = None,
    end_date: str | None = None,
    interval: str = "daily",
    output_path: str | None = None,
    style_name: str | None = None,
) -> dict[str, Any]:
    """
    Fetch a guarded FX series from LSEG and save a line chart PNG under outputs/.

    Args:
        pair: Allowed FX pair, such as USDJPY.
        start_date: Optional ISO date. Defaults to 90 days before end_date.
        end_date: Optional ISO date. Defaults to today.
        interval: daily, weekly, or monthly.
        output_path: Optional PNG output path under outputs/.
        style_name: Optional named chart style from the configured chart styles file.
    """

    history = get_lseg_fx_history(
        pair=pair,
        start_date=start_date,
        end_date=end_date,
        interval=interval,
    )
    if history["status"] != "success":
        return {
            "status": "error",
            "message": history["message"],
            "history": history,
            "chart": None,
        }

    results = history["results"]
    if not results:
        return {
            "status": "error",
            "message": f"No LSEG history returned for {history['pair']}.",
            "history": history,
            "chart": None,
        }

    chart = create_chart_png(
        chart_type="line",
        x_values=[item["date"] for item in results],
        y_values=[item["value"] for item in results],
        title=f"{history['pair']} LSEG history",
        output_path=output_path,
        x_label="Date",
        y_label=history["pair"],
        style_name=style_name,
    )

    return {
        "status": chart["status"],
        "message": chart.get("message", "Chart created."),
        "history": history,
        "chart": chart,
    }
