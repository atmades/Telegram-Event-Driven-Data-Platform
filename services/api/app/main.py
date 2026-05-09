from decimal import Decimal
from uuid import UUID
from datetime import datetime

from fastapi import FastAPI, Query

from app.db import fetch_expenses, fetch_expenses_summary


app = FastAPI(title="Telegram Event Platform API")


def serialize_row(row: dict) -> dict:
    result = {}

    for key, value in row.items():
        if isinstance(value, (datetime, UUID)):
            result[key] = str(value)
        elif isinstance(value, Decimal):
            result[key] = float(value)
        else:
            result[key] = value

    return result


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/expenses")
def get_expenses(limit: int = Query(default=20, ge=1, le=100)):
    rows = fetch_expenses(limit)
    return [serialize_row(dict(row)) for row in rows]


@app.get("/expenses/summary")
def get_expenses_summary():
    rows = fetch_expenses_summary()
    return [serialize_row(dict(row)) for row in rows]