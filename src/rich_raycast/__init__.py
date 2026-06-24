"""Small Rich helpers for Python Raycast Script Commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Literal

import tooltime
from rich.console import Console
from rich.text import Text

RaycastMode = Literal["inline", "compact", "fullOutput"]
Tone = Literal["success", "warning", "error", "info", "muted"]
DurationForm = Literal["compact", "phrase", "clock", "clock_phrase"]
BlockUnit = Literal["day", "hour", "minute", "week", "month"]
TimeAgoForm = Literal["compact", "phrase"]
DateForm = Literal["iso", "iso_pretty", "date", "date_compact"]
TimestampLike = datetime | int | float | str

DEFAULT_SEPARATOR = " | "
TONE_STYLES: dict[Tone, str] = {
    "success": "green",
    "warning": "yellow",
    "error": "bold red",
    "info": "cyan",
    "muted": "dim",
}


@dataclass(frozen=True, slots=True)
class Stat:
    """A labeled value for one-line Raycast output."""

    label: str
    value: object
    style: str | None = None
    label_style: str = ""


def raycast_console(
    *,
    highlight: bool = False,
    color_system: Literal[
        "auto", "standard", "256", "truecolor", "windows"
    ] = "truecolor",
    force_terminal: bool = True,
) -> Console:
    """Return a Rich console configured for Raycast script-command output."""

    return Console(
        force_terminal=force_terminal,
        color_system=color_system,
        highlight=highlight,
    )


console = raycast_console()


def now_label(value: TimestampLike | None = None) -> str:
    """Format a local timestamp for compact Raycast output."""

    refreshed_at = (
        _to_datetime(value) if value is not None else datetime.now().astimezone()
    )
    refreshed_at = refreshed_at.astimezone()
    time_label = refreshed_at.strftime("%I:%M %p").lstrip("0")
    return f"{refreshed_at.strftime('%b')} {refreshed_at.day}, {time_label}"


def money(
    amount: float | int | str | Decimal,
    *,
    currency: str = "$",
    places: int = 2,
    signed: bool = False,
) -> str:
    """Format a numeric value as money without adding style markup."""

    value = _to_decimal(amount)
    quantized = value.quantize(Decimal(10) ** -places, rounding=ROUND_HALF_UP)
    sign = ""
    if signed and quantized > 0:
        sign = "+"
    if quantized < 0:
        sign = "-"
        quantized = abs(quantized)
    return f"{sign}{currency}{quantized:,.{places}f}"


def balance_style(amount: float | int | str | Decimal) -> str:
    """Return green for non-negative balances and red for negative balances."""

    return "green" if _to_decimal(amount) >= 0 else "red"


def cost_style(amount: float | int | str | Decimal) -> str:
    """Return red for positive costs and green for negative costs."""

    return "red" if _to_decimal(amount) >= 0 else "green"


def stale_style(
    seconds_ago: float | int,
    *,
    fresh: float = 60.0,
    recent: float = 3600.0,
    stale: float = 86400.0,
) -> str:
    """Return a Rich color name describing data freshness.

    Tiers default to: <1m green, <1h cyan, <1d yellow, else red.
    """

    value = float(seconds_ago)
    if value < fresh:
        return "green"
    if value < recent:
        return "cyan"
    if value < stale:
        return "yellow"
    return "red"


def duration_label(
    seconds: float | int,
    *,
    form: DurationForm = "compact",
) -> str:
    """Format a length of time using tooltime's interconvertible timelength forms.

    - ``compact``     -> ``"15d"``       (``tooltime.timelength_seconds_to_label``)
    - ``phrase``      -> ``"15 days"``   (``tooltime.timelength_seconds_to_phrase``)
    - ``clock``       -> ``"3:0:10:10"`` (``tooltime.timelength_seconds_to_clock``)
    - ``clock_phrase``-> ``"3 days, 0:10:10"`` (``tooltime.timelength_seconds_to_clock_phrase``)
    """

    seconds_int = int(seconds)
    match form:
        case "compact":
            return tooltime.timelength_seconds_to_label(seconds_int)
        case "phrase":
            return tooltime.timelength_seconds_to_phrase(seconds_int)
        case "clock":
            return tooltime.timelength_seconds_to_clock(seconds_int)
        case "clock_phrase":
            return tooltime.timelength_seconds_to_clock_phrase(seconds_int)
        case _:
            raise ValueError(f"Unsupported duration form: {form!r}")


def date_label(
    timestamp: TimestampLike | None = None,
    *,
    form: DateForm = "iso",
) -> str:
    """Format a timestamp as a date using tooltime's date representations.

    Unlike ``now_label`` (local pretty form ``"Jun 24, 2:55 PM"``),
    ``date_label`` returns ISO/calendar forms suited to ``fullOutput``
    model tables and tabular listings.

    - ``iso``         -> ``"2020-09-13T12:26:40Z"`` (tooltime)
    - ``iso_pretty``  -> ``"2020-09-13 12:26:40Z"`` (tooltime)
    - ``date``        -> ``"2020-09-13"``            (tooltime)
    - ``date_compact``-> ``"20200913"``             (tooltime)
    """

    seconds = _to_seconds(timestamp) if timestamp is not None else _current_seconds()
    match form:
        case "iso":
            return tooltime.timestamp_seconds_to_iso(seconds)
        case "iso_pretty":
            return tooltime.timestamp_seconds_to_iso_pretty(seconds)
        case "date":
            return tooltime.timestamp_seconds_to_date(seconds)
        case "date_compact":
            return tooltime.timestamp_seconds_to_date_compact(seconds)
        case _:
            raise ValueError(f"Unsupported date form: {form!r}")


def compact_number(value: int | float | None, *, places: int = 1) -> str:
    """Abbreviate a large integer with ``k``/``M``/``B``/``T`` suffixes.

    ``None`` returns ``"-"`` to mirror the convention used by model-listing
    scripts when API fields are optional.
    """

    if value is None:
        return "-"
    try:
        value = float(value)
    except (TypeError, ValueError):
        return "-"

    abs_value = abs(value)
    sign = "-" if value < 0 else ""
    thresholds = [
        (1_000_000_000_000, "T"),
        (1_000_000_000, "B"),
        (1_000_000, "M"),
        (1_000, "k"),
    ]
    for threshold, suffix in thresholds:
        if abs_value >= threshold:
            scaled = abs_value / threshold
            if scaled == int(scaled):
                return f"{sign}{int(scaled)}{suffix}"
            return f"{sign}{scaled:.{places}f}{suffix}"
    if value == int(value):
        return f"{sign}{int(abs_value)}"
    return f"{sign}{abs_value:.{places}f}"


def truncate_text(text: str, width: int, *, ellipsis: str = "...") -> str:
    """Truncate ``text`` to ``width`` columns, appending ``ellipsis`` when cut."""

    if len(text) <= width:
        return text
    if width <= len(ellipsis):
        return ellipsis[:width]
    return text[: width - len(ellipsis)] + ellipsis


def time_ago(
    timestamp: TimestampLike,
    *,
    now: TimestampLike | None = None,
    form: TimeAgoForm = "compact",
) -> str:
    """Format how long ago a timestamp occurred, suitable for Raycast inline stats.

    Compact form uses a single largest unit: ``"just now"``, ``"5m ago"``,
    ``"3h ago"``, ``"2d ago"``. Beyond one week it falls back to the calendar
    date (``"Jun 24"``). Phrase form delegates to tooltime's
    ``timelength_seconds_to_phrase``.
    """

    then = _to_seconds(timestamp)
    now_seconds = _to_seconds(now) if now is not None else _current_seconds()
    delta = now_seconds - then
    if delta < 0:
        delta = 0

    if form == "phrase":
        return f"{tooltime.timelength_seconds_to_phrase(int(delta))} ago"

    if delta < 60:
        return "just now"
    if delta < 3600:
        return f"{int(delta // 60)}m ago"
    if delta < 86400:
        return f"{int(delta // 3600)}h ago"
    if delta < 604800:
        return f"{int(delta // 86400)}d ago"
    return _seconds_to_local_date_label(then)


def period_bounds(
    timestamp: TimestampLike | None = None,
    *,
    unit: BlockUnit = "day",
    block_size: int = 1,
) -> tuple[int, int]:
    """Return the ``(start, end)`` epoch-second bounds of the standardized
    block containing ``timestamp`` (defaults to now).

    Wraps ``tooltime.get_standard_timeperiod``. Useful for driving "this
    month's spend" / "today's usage" API calls in Raycast inline scripts.
    ``include_end`` uses the last second of the block (inclusive), matching
    how billing windows are conventionally expressed.
    """

    ts = _to_seconds(timestamp) if timestamp is not None else _current_seconds()
    timeperiod = tooltime.get_standard_timeperiod(
        timestamp=ts,
        block_unit=unit,
        block_size=block_size,
        include_start=True,
        include_end=False,
    )
    start = int(timeperiod["start"])
    end = int(timeperiod["end"])
    return start, end


def inline(
    *stats: Stat,
    refreshed_at: TimestampLike | bool | None = None,
    separator: str = DEFAULT_SEPARATOR,
) -> Text:
    """Build a one-line Rich Text payload for Raycast inline/compact modes."""

    pieces: list[Text] = [_render_stat(stat) for stat in stats]
    if refreshed_at:
        if refreshed_at is True:
            label: str = now_label()
        elif isinstance(refreshed_at, str):
            label = _maybe_parsed_label(refreshed_at)
        else:
            label = now_label(refreshed_at)
        pieces.append(
            _render_stat(Stat("Refreshed", label, style="dim", label_style="dim"))
        )

    output = Text()
    for index, piece in enumerate(pieces):
        if index:
            output.append(separator)
        output.append_text(piece)
    return output


def print_inline(
    *stats: Stat,
    refreshed_at: TimestampLike | bool | None = None,
    separator: str = DEFAULT_SEPARATOR,
    target: Console | None = None,
) -> None:
    """Print a Raycast-friendly one-line stats payload."""

    (target or console).print(
        inline(*stats, refreshed_at=refreshed_at, separator=separator)
    )


def print_status(
    message: object,
    *,
    tone: Tone = "info",
    target: Console | None = None,
) -> None:
    """Print a short status line with a conventional Raycast color."""

    (target or console).print(str(message), style=TONE_STYLES[tone])


def print_error(message: object, *, target: Console | None = None) -> None:
    """Print a conventional Raycast error line."""

    print_status(message, tone="error", target=target)


def die(message: object, *, target: Console | None = None) -> None:
    """Print an error line in Raycast style and exit the script.

    Use to bail out of a Script Command when a required env var is missing
    or the API shape is unexpected. Raycast reads the last line of stdout
    as the error toast when the script exits non-zero, so callers should
    invoke ``die`` last.
    """

    print_error(message, target=target)
    raise SystemExit(1)


def print_request_error(exc: BaseException, *, target: Console | None = None) -> None:
    """Print a conventional error line for an HTTP/JSON request exception.

    Duck-types ``exc`` so callers can hand it ``httpx.RequestError``,
    ``httpx.HTTPStatusError``, ``json.JSONDecodeError`` / ``ValueError``,
    or any other request-layer exception without this library importing
    httpx. Mirrors the 5-hand-clause block repeated across Cerebras/Groq/
    OpenCodeZen/Openrouter/xAI scripts.
    """

    response = getattr(exc, "response", None)
    if response is not None:
        status = getattr(response, "status_code", "?")
        text = getattr(response, "text", "")
        print_error(f"API returned {status}: {text}", target=target)
    elif isinstance(exc, ValueError):
        print_error("API returned invalid JSON.", target=target)
    else:
        print_error(f"Network error: {exc}", target=target)


def _render_stat(stat: Stat) -> Text:
    text = Text()
    label_style = stat.label_style
    value_style = stat.style or ""
    text.append(f"{stat.label}: ", style=label_style)
    text.append(str(stat.value), style=value_style)
    return text


def _to_decimal(value: float | int | str | Decimal) -> Decimal:
    if isinstance(value, Decimal):
        return value
    try:
        return Decimal(str(value))
    except InvalidOperation as exc:
        raise ValueError(f"Expected a numeric value, got {value!r}") from exc


def _to_seconds(value: TimestampLike) -> int:
    if isinstance(value, datetime):
        return int(value.timestamp())
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return int(tooltime.timestamp_to_seconds(value))
    raise ValueError(f"Unsupported timestamp value: {value!r}")


def _to_datetime(value: TimestampLike) -> datetime:
    if isinstance(value, datetime):
        return value
    seconds = _to_seconds(value)
    return datetime.fromtimestamp(seconds, tz=timezone.utc)


def _current_seconds() -> int:
    return int(tooltime.now("TimestampSeconds"))


def _seconds_to_local_date_label(seconds: int) -> str:
    return datetime.fromtimestamp(seconds).astimezone().strftime("%b %-d")


def _maybe_parsed_label(value: str) -> str:
    """Use a string as a pre-formatted Refreshed label, or parse it with tooltime."""

    try:
        return now_label(value)
    except Exception:
        return value


__all__ = [
    "BlockUnit",
    "DateForm",
    "DurationForm",
    "Stat",
    "balance_style",
    "compact_number",
    "console",
    "cost_style",
    "date_label",
    "die",
    "duration_label",
    "inline",
    "money",
    "now_label",
    "period_bounds",
    "print_error",
    "print_inline",
    "print_request_error",
    "print_status",
    "raycast_console",
    "stale_style",
    "time_ago",
    "truncate_text",
]
