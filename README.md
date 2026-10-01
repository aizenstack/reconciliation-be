# Data Reconciliation API

Backend service for comparing application stock Excel files against real stock data, matching by **SKU**, and generating corrected exports.

**Author:** [Febrian Yosi Pangestu](https://github.com/aizenstack)

## Setup

```bash
cd reconciliation-be
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

See also: [CHANGELOG.md](CHANGELOG.md), [LICENCE.md](LICENCE.md), [SECURITY.md](SECURITY.md).
