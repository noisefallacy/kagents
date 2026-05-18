import sys
import types

import pandas as pd

from kagents.config import PROJECT_ROOT
from kagents.tools import lseg
from kagents.tools.lseg import get_lseg_fx_history, plot_lseg_fx_history


class FakeSession:
    def open(self) -> None:
        pass

    def close(self) -> None:
        pass


class FakeDefinition:
    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def get_session(self):
        return FakeSession()


class FakeGrantPassword:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


class FakeLd:
    def __init__(self):
        platform = types.SimpleNamespace(
            Definition=FakeDefinition,
            GrantPassword=FakeGrantPassword,
        )
        self.session = types.SimpleNamespace(
            platform=platform,
            set_default=lambda session: None,
        )

    def get_history(self, **kwargs):
        index = pd.to_datetime(["2026-05-01", "2026-05-02"])
        return pd.DataFrame({"JPY=": [154.1, 154.5]}, index=index)


def install_fake_lseg(monkeypatch):
    fake_ld = FakeLd()
    lseg_data_module = types.ModuleType("lseg.data")
    lseg_data_module.session = fake_ld.session
    lseg_data_module.get_history = fake_ld.get_history
    lseg_data_module.open_session = lambda: FakeSession()

    lseg_module = types.ModuleType("lseg")
    lseg_module.data = lseg_data_module

    monkeypatch.setitem(sys.modules, "lseg", lseg_module)
    monkeypatch.setitem(sys.modules, "lseg.data", lseg_data_module)


def configure_lseg(monkeypatch):
    monkeypatch.setattr(
        lseg,
        "settings",
        types.SimpleNamespace(
            lseg_session_method="remote",
            lseg_app_key="app-key",
            lseg_username="user",
            lseg_password="pass",
        ),
    )


def test_get_lseg_fx_history_returns_series(monkeypatch) -> None:
    install_fake_lseg(monkeypatch)
    configure_lseg(monkeypatch)

    result = get_lseg_fx_history(
        pair="USDJPY",
        start_date="2026-05-01",
        end_date="2026-05-02",
    )

    assert result["status"] == "success"
    assert result["pair"] == "USDJPY"
    assert result["ric"] == "JPY="
    assert result["results"][0]["value"] == 154.1


def test_get_lseg_fx_history_rejects_unsupported_pair() -> None:
    result = get_lseg_fx_history(pair="FOOBAR")

    assert result["status"] == "error"
    assert "Unsupported FX pair" in result["message"]


def test_get_lseg_fx_history_requires_credentials(monkeypatch) -> None:
    monkeypatch.setattr(
        lseg,
        "settings",
        types.SimpleNamespace(
            lseg_session_method="remote",
            lseg_app_key=None,
            lseg_username=None,
            lseg_password=None,
        ),
    )

    result = get_lseg_fx_history(pair="USDJPY")

    assert result["status"] == "error"
    assert "credentials" in result["message"]


def test_plot_lseg_fx_history_creates_png(monkeypatch) -> None:
    install_fake_lseg(monkeypatch)
    configure_lseg(monkeypatch)

    output_path = PROJECT_ROOT / "outputs" / "test_usdjpy_lseg.png"
    if output_path.exists():
        output_path.unlink()

    result = plot_lseg_fx_history(
        pair="USDJPY",
        start_date="2026-05-01",
        end_date="2026-05-02",
        output_path="outputs/test_usdjpy_lseg.png",
    )

    assert result["status"] == "success"
    assert result["history"]["row_count"] == 2
    assert output_path.exists()

    output_path.unlink()
