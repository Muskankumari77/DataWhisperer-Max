from __future__ import annotations

import io
import json
import sqlite3
from typing import Any

import pandas as pd


def load_csv(file) -> pd.DataFrame:
    return pd.read_csv(file)


def load_excel(file) -> dict[str, pd.DataFrame]:
    book = pd.ExcelFile(file)
    return {sheet: pd.read_excel(book, sheet_name=sheet) for sheet in book.sheet_names}


def load_json(file) -> pd.DataFrame:
    raw = json.load(file)
    if isinstance(raw, list):
        return pd.json_normalize(raw)
    if isinstance(raw, dict):
        # Handle common {data: [...]} API responses.
        for key in ("data", "results", "records", "items"):
            if isinstance(raw.get(key), list):
                return pd.json_normalize(raw[key])
        return pd.json_normalize(raw)
    raise ValueError("JSON must contain an object or an array of records.")


def extract_pdf_tables(file) -> dict[str, pd.DataFrame]:
    import pdfplumber

    file.seek(0)
    tables: dict[str, pd.DataFrame] = {}
    with pdfplumber.open(file) as pdf:
        for page_no, page in enumerate(pdf.pages, start=1):
            for table_no, table in enumerate(page.extract_tables() or [], start=1):
                if not table:
                    continue
                rows = [row for row in table if row and any(str(x or "").strip() for x in row)]
                if len(rows) < 2:
                    continue
                header = [str(x or "").strip() for x in rows[0]]
                body = rows[1:]
                # Make duplicate/blank headers usable.
                seen: dict[str, int] = {}
                clean_header = []
                for i, col in enumerate(header):
                    base = col or f"column_{i+1}"
                    seen[base] = seen.get(base, 0) + 1
                    clean_header.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
                df = pd.DataFrame(body, columns=clean_header)
                tables[f"Page {page_no} · Table {table_no}"] = df
    if not tables:
        raise ValueError("No readable tables were found in this PDF.")
    return tables


def sqlite_tables(file) -> list[str]:
    file.seek(0)
    raw = file.read()
    conn = sqlite3.connect(":memory:")
    try:
        conn.executescript("PRAGMA query_only = ON;")
        # SQLite has no direct stream database loading, so backup from a temp file.
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
            tmp.write(raw)
            path = tmp.name
        src = sqlite3.connect(path)
        try:
            src.backup(conn)
        finally:
            src.close()
        return [r[0] for r in conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
    finally:
        conn.close()


def load_sqlite_table(file, table: str) -> pd.DataFrame:
    file.seek(0)
    raw = file.read()
    import tempfile
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        tmp.write(raw)
        path = tmp.name
    conn = sqlite3.connect(path)
    try:
        safe = table.replace('"', '""')
        return pd.read_sql_query(f'SELECT * FROM "{safe}"', conn)
    finally:
        conn.close()


def postgres_engine(host: str, port: int, database: str, username: str, password: str):
    from sqlalchemy import create_engine
    from urllib.parse import quote_plus

    url = (
        f"postgresql+psycopg2://{quote_plus(username)}:{quote_plus(password)}"
        f"@{host}:{int(port)}/{database}"
    )
    return create_engine(url, pool_pre_ping=True, connect_args={"connect_timeout": 5})


def inspect_postgres(host: str, port: int, database: str, username: str, password: str) -> list[str]:
    from sqlalchemy import inspect

    engine = postgres_engine(host, port, database, username, password)
    try:
        inspector = inspect(engine)
        return inspector.get_table_names(schema="public")
    finally:
        engine.dispose()


def load_postgres_table(host: str, port: int, database: str, username: str, password: str, table: str) -> pd.DataFrame:
    from sqlalchemy import text

    engine = postgres_engine(host, port, database, username, password)
    try:
        # Identifier is safely quoted; table comes from inspect_postgres selection.
        safe = table.replace('"', '""')
        with engine.connect() as conn:
            return pd.read_sql(text(f'SELECT * FROM "public"."{safe}"'), conn)
    finally:
        engine.dispose()
