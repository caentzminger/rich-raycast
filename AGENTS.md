# rich-raycast

Tiny Python package of Rich helpers for Raycast Script Commands.

## Tooling

- **Package manager / build**: `uv` with `uv_build` backend.
- **Dev tools**: `pytest`, `ruff`, `ty` (type checker).
- **Python**: `>=3.12`.
- **Layout**: source layout under `src/rich_raycast/`.

## Common commands

```bash
uv run pytest          # run tests
uv run ruff check .    # lint
uv run ruff format .   # format
uv run ty              # type check
```

## Notes

- This package is typically consumed as a `uv` script dependency in Raycast Script Commands, referenced by absolute file path (see `README.md` example).
- No custom `pytest.ini`, `ruff.toml`, or tool sections in `pyproject.toml` — all tools run with defaults.
- `py.typed` is present; the package is typed.
