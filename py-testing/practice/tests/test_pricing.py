from decimal import Decimal
from unittest.mock import Mock, patch

import pytest

from study_app.pricing import price_in_rubles

pytestmark = pytest.mark.unit


def test_price_uses_configured_rate():
    with patch("study_app.pricing.getenv", autospec=True, return_value="100") as getenv:
        result = price_in_rubles(Decimal("2.5"))
    assert result == Decimal("250")
    getenv.assert_called_once_with("USD_RATE", "90")


def test_negative_amount_does_not_read_configuration():
    with patch("study_app.pricing.getenv", autospec=True) as getenv:
        with pytest.raises(ValueError, match="amount must not be negative"):
            price_in_rubles(Decimal("-1"))
    getenv.assert_not_called()


def test_configuration_failure_propagates():
    with patch("study_app.pricing.getenv", side_effect=OSError("configuration unavailable")):
        with pytest.raises(OSError, match="configuration unavailable"):
            price_in_rubles(Decimal("1"))


@pytest.mark.parametrize("rate", ["0", "-1"])
def test_nonpositive_rate_is_rejected(monkeypatch, rate):
    monkeypatch.setenv("USD_RATE", rate)
    with pytest.raises(ValueError, match="rate must be positive"):
        price_in_rubles(Decimal("1"))


def test_mock_can_use_a_function_side_effect():
    lookup = Mock(side_effect=lambda key: {"USD_RATE": "100"}[key])
    with patch("study_app.pricing.getenv", side_effect=lambda key, default: lookup(key)):
        assert price_in_rubles(Decimal("3")) == Decimal("300")
    lookup.assert_called_once_with("USD_RATE")
