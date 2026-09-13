# DataWhisperer AI MAX

A polished Streamlit data-intelligence workspace. Bring in CSV, Excel, JSON, PDF tables, SQLite or PostgreSQL data, then ask questions in plain English.

## Run on Windows PowerShell

```powershell
cd "$HOME\OneDrive\Desktop\DataWhisperer-AI-MAX"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
Copy-Item .env.example .env
streamlit run app.py
```

Edit `.env` and add your Groq key. The default Groq model is `openai/gpt-oss-120b`.

For PostgreSQL, use the same host/port/database/user/password that work in pgAdmin. The app inspects the public schema, lets you select a table, and loads it read-only with SQLAlchemy.

## Supported sources

- CSV
- Excel
- JSON
- PDF tables
- SQLite
- PostgreSQL

## AI providers

- Groq through its OpenAI-compatible API
- OpenAI API

The AI layer generates pandas/matplotlib analysis code. A restricted AST validator blocks imports, file/network access, shell execution and other unsafe constructs before execution.
