"""Small Rich helpers for Python Raycast Script Commands."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from typing import Literal

from rich.console import Console
from rich.text import Text

RaycastMode = Literal["inline", "compact", "fullOutput"]
Tone = Literal["success", "warning", "error", "info", "muted"]

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


def now_label(value: datetime | None = None) -> str:
    """Format a local timestamp for compact Raycast output."""

    refreshed_at = (value or datetime.now().astimezone()).astimezone()
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


def inline(
    *stats: Stat,
    refreshed_at: datetime | str | bool | None = None,
    separator: str = DEFAULT_SEPARATOR,
) -> Text:
    """Build a one-line Rich Text payload for Raycast inline/compact modes."""

    pieces: list[Text] = [_render_stat(stat) for stat in stats]
    if refreshed_at:
        label = (
            now_label()
            if refreshed_at is True
            else (
                now_label(refreshed_at)
                if isinstance(refreshed_at, datetime)
                else refreshed_at
            )
        )
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
    refreshed_at: datetime | str | bool | None = None,
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


__all__ = [
    "Stat",
    "balance_style",
    "console",
    "cost_style",
    "inline",
    "money",
    "now_label",
    "print_error",
    "print_inline",
    "print_status",
    "raycast_console",
]
