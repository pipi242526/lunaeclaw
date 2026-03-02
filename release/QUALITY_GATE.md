# Incremental Quality Gate

This project does **not** require one-shot cleanup of all historical lint debt.

It enforces a practical gate:

- New/changed Python files must pass lint.
- Existing legacy warnings can be cleaned progressively.

## Commands

```bash
# Run changed-file lint against release/lint-baseline.txt (or origin/main fallback)
python scripts/lint_changed.py

# Full tests
uv run pytest -q
```

Baseline pin:

- `release/lint-baseline.txt` defines the technical-debt freeze point.
- Update it only after intentional debt cleanup.

## CI Recommendation

Use the same changed-file lint command in your CI pipeline to block regressions without blocking iterative refactors.
