# ledger-engine

Thread-safe double-entry ledger with balanced, idempotent atomic posting.

## Requirements

Python 3.11+ · Standard library only.

## Test

```sh
python -m unittest discover -s . -p 'test_core.py' -v
```

## Contents

- `core.py` implementation
- `test_core.py` unit tests
- `.github/workflows/tests.yml` CI matrix (Python 3.11–3.13)

## Scope

Educational/portfolio reference implementation, not an audited production service. Further review is required for deployment.
