from __future__ import annotations

from datetime import datetime
from zoneinfo import ZoneInfo

import pytest

from rich_raycast import Stat, balance_style, cost_style, inline, money, now_label


def test_money_formats_decimal_places_and_grouping() -> None:
    assert money("1234.565") == "$1,234.57"


def test_money_can_emit_explicit_positive_sign() -> None:
    assert money(12, signed=True) == "+$12.00"
    assert money(-12, signed=True) == "-$12.00"


def test_styles_follow_balance_and_cost_conventions() -> None:
    assert balance_style(0) == "green"
    assert balance_style("-0.01") == "red"
    assert cost_style(0) == "red"
    assert cost_style("-0.01") == "green"


def test_now_label_uses_localized_month_day_time_shape() -> None:
    value = datetime(2026, 6, 24, 14, 55, tzinfo=ZoneInfo("America/Chicago"))
    assert now_label(value) == "Jun 24, 2:55 PM"


def test_inline_renders_stats_and_refreshed_label_as_plain_text() -> None:
    rendered = inline(
        Stat("Remaining", money(12.34), style="green"),
        Stat("This Month", money(5.67), style="red"),
        refreshed_at="Jun 24, 2:55 PM",
    )

    assert rendered.plain == (
        "Remaining: $12.34 | This Month: $5.67 | Refreshed: Jun 24, 2:55 PM"
    )


def test_money_rejects_non_numeric_values() -> None:
    with pytest.raises(ValueError, match="Expected a numeric value"):
        money("nope")
