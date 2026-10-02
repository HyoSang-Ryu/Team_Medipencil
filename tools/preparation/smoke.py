"""Generic dependency smoke only: no product data, routes, schema or AI."""
import json
import platform
import sqlite3
from importlib.metadata import version

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, text


class Echo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: int


app = FastAPI()


@app.post("/echo")
def echo(body: Echo):
    return body


with TestClient(app) as client:
    assert client.post("/echo", json={"value": 7}).json() == {"value": 7}
    assert client.post("/echo", json={"value": 7, "extra": 1}).status_code == 422

engine = create_engine("sqlite://")
with engine.connect() as connection:
    connection.execute(text("PRAGMA foreign_keys=ON"))
    assert connection.scalar(text("PRAGMA foreign_keys")) == 1
    connection.execute(text("CREATE TABLE smoke (value INTEGER NOT NULL)"))
    connection.commit()
    connection.execute(text("INSERT INTO smoke VALUES (7)"))
    connection.rollback()
    assert connection.scalar(text("SELECT COUNT(*) FROM smoke")) == 0
engine.dispose()
print(json.dumps({
    "scope": "GENERIC_ENVIRONMENT_ONLY",
    "python": platform.python_version(),
    "sqlite": sqlite3.sqlite_version,
    "dependencies": {name: version(name) for name in
                     ("fastapi", "pydantic", "SQLAlchemy", "alembic", "httpx", "pytest", "uvicorn")},
    "checks": {"echo": "PASS", "extra_field_rejected": "PASS", "rollback": "PASS"},
    "product_tests": "NOT_RUN", "AI_calls": 0,
}, indent=2))
