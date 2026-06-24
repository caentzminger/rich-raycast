from __future__ import annotations

from datetime import datetime
from typing import Any, cast
from zoneinfo import ZoneInfo

import pytest

from rich_raycast import (
    DateForm,
    DurationForm,
    Stat,
    balance_style,
    compact_number,
    cost_style,
    date_label,
    die,
    duration_label,
    inline,
    money,
    now_label,
    period_bounds,
    print_request_error,
    stale_style,
    time_ago,
    truncate_text,
)

NOW_EPOCH = 1719268800


def test_money_formats_decimal_places_and_grouping() -> None:
    assert money("1234.565") == "$1,234.57"


def test_money_can_emit_explicit_positive_sign() -> None:
    assert money(12, signed=True) == "+$12.00"
    assert money(-12, signed=True) == "-$12.00"


def test_money_rejects_non_numeric_values() -> None:
    with pytest.raises(ValueError, match="Expected a numeric value"):
        money("nope")


def test_styles_follow_balance_and_cost_conventions() -> None:
    assert balance_style(0) == "green"
    assert balance_style("-0.01") == "red"
    assert cost_style(0) == "red"
    assert cost_style("-0.01") == "green"


def test_stale_style_returns_four_color_tiers_by_default() -> None:
    assert stale_style(30) == "green"
    assert stale_style(300) == "cyan"
    assert stale_style(3 * 3600) == "yellow"
    assert stale_style(2 * 86400) == "red"


def test_stale_style_honors_custom_thresholds() -> None:
    assert stale_style(5, fresh=10, recent=100, stale=1000) == "green"


def test_now_label_accepts_datetime_epoch_float_and_iso_string() -> None:
    fixed = datetime(2026, 6, 24, 14, 55, tzinfo=ZoneInfo("America/Chicago"))
    assert now_label(fixed) == "Jun 24, 2:55 PM"
    # 1600000000 = 2020-09-13T12:26:40Z
    assert now_label(1600000000) == "Sep 13, 7:26 AM"
    assert now_label(float(1600000000)) == "Sep 13, 7:26 AM"
    assert now_label("2020-09-13T12:26:40Z") == "Sep 13, 7:26 AM"


def test_duration_label_supports_all_four_forms() -> None:
    assert duration_label(15 * 86400) == "15d"
    assert duration_label(15 * 86400, form="phrase") == "15 days"
    assert duration_label(3 * 86400 + 610, form="clock") == "3:0:10:10"
    assert duration_label(3 * 86400 + 610, form="clock_phrase") == "3 days, 0:10:10"


def test_duration_label_rejects_unknown_forms() -> None:
    with pytest.raises(ValueError, match="Unsupported duration form"):
        duration_label(60, form=cast(DurationForm, "nonsense"))


def test_time_ago_compact_form_uses_single_largest_unit() -> None:
    assert time_ago(NOW_EPOCH - 30, now=NOW_EPOCH) == "just now"
    assert time_ago(NOW_EPOCH - 5 * 60, now=NOW_EPOCH) == "5m ago"
    assert time_ago(NOW_EPOCH - 3 * 3600, now=NOW_EPOCH) == "3h ago"
    assert time_ago(NOW_EPOCH - 2 * 86400, now=NOW_EPOCH) == "2d ago"


def test_time_ago_falls_back_to_calendar_date_beyond_one_week() -> None:
    label = time_ago(NOW_EPOCH - 12 * 86400, now=NOW_EPOCH)
    assert label.count(" ") == 1
    assert label.startswith(
        (
            "Jan",
            "Feb",
            "Mar",
            "Apr",
            "May",
            "Jun",
            "Jul",
            "Aug",
            "Sep",
            "Oct",
            "Nov",
            "Dec",
        )
    )


def test_time_ago_phrase_form_delegates_to_tooltime() -> None:
    assert time_ago(NOW_EPOCH - 300, now=NOW_EPOCH, form="phrase") == "5 minutes ago"


def test_period_bounds_day_window_starts_at_local_midnight_utc() -> None:
    assert period_bounds(1600000000, unit="day") == (1599955200, 1600041599)


def test_period_bounds_has_inclusive_end_terminal_second() -> None:
    start, end = period_bounds(1600000000, unit="hour")
    assert start <= 1600000000 <= end
    assert end > start


def test_inline_renders_stats_and_refreshed_label_as_plain_text() -> None:
    rendered = inline(
        Stat("Remaining", money(12.34), style="green"),
        Stat("This Month", money(5.67), style="red"),
        refreshed_at="Jun 24, 2:55 PM",
    )
    assert rendered.plain == (
        "Remaining: $12.34 | This Month: $5.67 | Refreshed: Jun 24, 2:55 PM"
    )


def test_inline_accepts_epoch_int_refreshed_at() -> None:
    rendered = inline(
        Stat("Remaining", money(12.34), style="green"),
        refreshed_at=1600000000,
    )
    assert "Sep 13" in rendered.plain


def test_inline_accepts_iso_string_refreshed_at() -> None:
    rendered = inline(
        Stat("Remaining", money(12.34)),
        refreshed_at="2020-09-13T12:26:40Z",
    )
    assert "Sep 13" in rendered.plain


def test_date_label_round_trips_epoch_to_iso_date_compact_forms() -> None:
    assert date_label(1600000000) == "2020-09-13T12:26:40Z"
    assert date_label(1600000000, form="iso_pretty") == "2020-09-13 12:26:40Z"
    assert date_label(1600000000, form="date") == "2020-09-13"
    assert date_label(1600000000, form="date_compact") == "20200913"


def test_date_label_rejects_unknown_forms() -> None:
    with pytest.raises(ValueError, match="Unsupported date form"):
        date_label(1600000000, form=cast(DateForm, "nonsense"))


def test_compact_number_abbreviates_thresholds() -> None:
    assert compact_number(0) == "0"
    assert compact_number(999) == "999"
    assert compact_number(1_500) == "1.5k"
    assert compact_number(1_000_000) == "1M"
    assert compact_number(1_500_000) == "1.5M"
    assert compact_number(1_000_000_000) == "1B"
    assert compact_number(1_500_000_000_000) == "1.5T"


def test_compact_number_handles_optional_and_invalid_inputs() -> None:
    assert compact_number(None) == "-"
    assert compact_number(cast(Any, "not a number")) == "-"


def test_compact_number_handles_signed_values() -> None:
    assert compact_number(-1_500) == "-1.5k"
    assert compact_number(-1_000_000) == "-1M"


def test_truncate_text_is_noop_below_width_and_appends_ellipsis_above() -> None:
    assert truncate_text("hello", 10) == "hello"
    assert truncate_text("hello world", 8) == "hello..."
    assert truncate_text("hello world", 10) == "hello w..."


def test_truncate_text_honors_custom_ellipsis() -> None:
    assert truncate_text("hello world", 9, ellipsis="…") == "hello wo…"


def test_die_prints_error_and_raises_systemexit(
    capsys: pytest.CaptureFixture[str],
) -> None:
    with pytest.raises(SystemExit) as excinfo:
        die("missing token")
    assert excinfo.value.code == 1
    captured = capsys.readouterr()
    assert "missing token" in captured.out


def test_print_request_error_handles_response_bearing_exception(
    capsys: pytest.CaptureFixture[str],
) -> None:
    class FakeResponse:
        status_code = 503
        text = "upstream down"

    class FakeHTTPError(Exception):
        def __init__(self) -> None:
            self.response = FakeResponse()

    print_request_error(FakeHTTPError())
    captured = capsys.readouterr()
    assert "503" in captured.out
    assert "upstream down" in captured.out


def test_print_request_error_handles_value_error_as_invalid_json(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_request_error(ValueError("bad json"))
    captured = capsys.readouterr()
    assert "invalid JSON" in captured.out


def test_print_request_error_falls_back_to_network_message(
    capsys: pytest.CaptureFixture[str],
) -> None:
    print_request_error(ConnectionError("timeout"))
    captured = capsys.readouterr()
    assert "Network error" in captured.out
    assert "timeout" in captured.out
