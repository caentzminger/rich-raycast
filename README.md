# rich-raycast

Tiny convenience helpers for Python Raycast Script Commands that already use
Rich, especially inline scripts that should emit compact, colored, readable
status text.

## Install in a uv script command

```python
# /// script
# requires-python = ">=3.12"
# dependencies = [
#     "rich-raycast @ file:///Users/cole/raycast/rich-raycast",
# ]
# ///
```

## Inline credits example

```python
from rich_raycast import Stat, balance_style, money, print_error, print_inline


def main() -> None:
    remaining = 12.34
    month_spend = 5.67

    print_inline(
        Stat("Remaining", money(remaining), style=balance_style(remaining)),
        Stat("This Month", money(month_spend), style="red"),
        refreshed_at=True,
    )
```

That prints the same kind of Raycast inline output as:

```text
Remaining: $12.34 | This Month: $5.67 | Refreshed: Jun 24, 2:55 PM
```

with Rich color applied to the values.

## API

- `raycast_console()`: returns `Console(force_terminal=True, color_system="truecolor", highlight=False)`.
- `console`: a default Raycast-configured console.
- `Stat`: a label/value/style tuple for compact inline output.
- `inline(...)`: builds a Rich `Text` object for one-line output.
- `print_inline(...)`: prints `inline(...)` through the default console.
- `now_label(...)`: formats local timestamps like `Jun 24, 2:55 PM`.
- `money(...)`: formats numeric values as currency without Rich markup.
- `balance_style(...)`: returns `green` for non-negative values, else `red`.
- `cost_style(...)`: returns `red` for non-negative values, else `green`.
- `print_status(...)` / `print_error(...)`: conventional short status lines.
