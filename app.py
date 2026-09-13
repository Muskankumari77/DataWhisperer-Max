from __future__ import annotations

import os
from pathlib import Path

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from services.ai import generate_code, explain_result
from services.analyzer import dataset_context, execute_analysis_code
from services.loaders import (
    extract_pdf_tables,
    inspect_postgres,
    load_csv,
    load_excel,
    load_json,
    load_postgres_table,
    load_sqlite_table,
    sqlite_tables,
)
from ui.styles import inject_css


# ============================================================
# CONFIG
# ============================================================

load_dotenv(Path(__file__).with_name(".env"))

st.set_page_config(
    page_title="DataWhisperer AI MAX",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# SESSION STATE
# ============================================================

if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if "df" not in st.session_state:
    st.session_state.df = None

if "source_name" not in st.session_state:
    st.session_state.source_name = ""

if "chat" not in st.session_state:
    st.session_state.chat = []

if "pg_tables" not in st.session_state:
    st.session_state.pg_tables = []


inject_css(st.session_state.theme)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        '<div class="dw-brand"><div class="dw-brand-mark">▤</div><div><div class="dw-brand-name">DataWhisperer <span>AI</span></div><div class="dw-brand-sub">Talk to your data in plain English</div></div></div>',
        unsafe_allow_html=True,
    )

    if st.button(
        "＋ New analysis",
        type="primary",
        width="stretch",
    ):
        st.session_state.df = None
        st.session_state.source_name = ""
        st.session_state.chat = []
        st.session_state.pg_tables = []
        st.rerun()

    st.markdown(
        '<div class="dw-side-title">DATA SOURCES</div>',
        unsafe_allow_html=True,
    )

    source = st.radio(
        "Source",
        [
            "CSV",
            "Excel",
            "JSON",
            "PDF Tables",
            "SQLite",
            "PostgreSQL",
        ],
        label_visibility="collapsed",
    )


    # ========================================================
    # CSV
    # ========================================================

    if source == "CSV":

        uploaded = st.file_uploader(
            "Upload CSV",
            type=["csv"],
        )

        if uploaded:

            try:
                st.session_state.df = load_csv(uploaded)
                st.session_state.source_name = uploaded.name

            except Exception as e:
                st.error(str(e))


    # ========================================================
    # EXCEL
    # ========================================================

    elif source == "Excel":

        uploaded = st.file_uploader(
            "Upload Excel",
            type=["xlsx", "xls"],
        )

        if uploaded:

            try:
                sheets = load_excel(uploaded)

                sheet = st.selectbox(
                    "Sheet",
                    list(sheets),
                )

                if st.button(
                    "Load Excel sheet",
                    type="primary",
                    width="stretch",
                ):
                    st.session_state.df = sheets[sheet]
                    st.session_state.source_name = (
                        f"{uploaded.name} · {sheet}"
                    )

            except Exception as e:
                st.error(str(e))


    # ========================================================
    # JSON
    # ========================================================

    elif source == "JSON":

        uploaded = st.file_uploader(
            "Upload JSON",
            type=["json"],
        )

        if uploaded:

            try:
                st.session_state.df = load_json(uploaded)
                st.session_state.source_name = uploaded.name

            except Exception as e:
                st.error(str(e))


    # ========================================================
    # PDF TABLES
    # ========================================================

    elif source == "PDF Tables":

        uploaded = st.file_uploader(
            "Upload PDF",
            type=["pdf"],
        )

        if uploaded:

            try:
                tables = extract_pdf_tables(uploaded)

                if tables:

                    key = st.selectbox(
                        "Table",
                        list(tables),
                    )

                    if st.button(
                        "Load PDF table",
                        type="primary",
                        width="stretch",
                    ):
                        st.session_state.df = tables[key]
                        st.session_state.source_name = (
                            f"{uploaded.name} · {key}"
                        )

                else:
                    st.warning(
                        "No tables were found in this PDF."
                    )

            except Exception as e:
                st.error(str(e))


    # ========================================================
    # SQLITE
    # ========================================================

    elif source == "SQLite":

        uploaded = st.file_uploader(
            "Upload SQLite database",
            type=["db", "sqlite", "sqlite3"],
        )

        if uploaded:

            try:
                tables = sqlite_tables(uploaded)

                if tables:

                    table = st.selectbox(
                        "Table",
                        tables,
                    )

                    if st.button(
                        "Load SQLite table",
                        type="primary",
                        width="stretch",
                    ):
                        st.session_state.df = load_sqlite_table(
                            uploaded,
                            table,
                        )

                        st.session_state.source_name = (
                            f"SQLite · {table}"
                        )

                else:
                    st.warning(
                        "No tables were found in this database."
                    )

            except Exception as e:
                st.error(str(e))


    # ========================================================
    # POSTGRESQL
    # ========================================================

    else:

        st.caption(
            "Credentials stay in this Streamlit session and are not stored by DataWhisperer."
        )

        pg_host = st.text_input(
            "Host",
            value="localhost",
        )

        pg_port = st.number_input(
            "Port",
            min_value=1,
            max_value=65535,
            value=5432,
            step=1,
        )

        pg_db = st.text_input(
            "Database",
            value="datawhisperer",
        )

        pg_user = st.text_input(
            "Username",
            value="postgres",
        )

        pg_password = st.text_input(
            "Password",
            type="password",
        )

        if st.button(
            "Inspect PostgreSQL",
            type="primary",
            width="stretch",
        ):

            try:

                st.session_state.pg_tables = inspect_postgres(
                    pg_host,
                    pg_port,
                    pg_db,
                    pg_user,
                    pg_password,
                )

                st.success(
                    f"Connected · "
                    f"{len(st.session_state.pg_tables)} tables"
                )

            except Exception as e:

                st.error(
                    f"Could not connect to PostgreSQL: {e}"
                )

        if st.session_state.pg_tables:

            pg_table = st.selectbox(
                "Select table",
                st.session_state.pg_tables,
            )

            if st.button(
                "Load PostgreSQL table",
                type="primary",
                width="stretch",
            ):

                try:

                    st.session_state.df = load_postgres_table(
                        pg_host,
                        pg_port,
                        pg_db,
                        pg_user,
                        pg_password,
                        pg_table,
                    )

                    st.session_state.source_name = (
                        f"PostgreSQL · {pg_table}"
                    )

                except Exception as e:

                    st.error(
                        f"Could not load table: {e}"
                    )


    # ========================================================
    # AI PROVIDER
    # ========================================================

    st.markdown(
        '<div class="dw-side-title">AI PROVIDER</div>',
        unsafe_allow_html=True,
    )

    provider = st.selectbox(
        "AI provider",
        ["Groq", "OpenAI"],
        label_visibility="collapsed",
    )

    provider_key = provider.lower()

    if (
        provider_key == "groq"
        and not os.getenv("GROQ_API_KEY")
    ):
        st.caption(
            "Add GROQ_API_KEY to .env to enable AI analysis."
        )

    if (
        provider_key == "openai"
        and not os.getenv("OPENAI_API_KEY")
    ):
        st.caption(
            "Add OPENAI_API_KEY to .env to enable AI analysis."
        )


    # ========================================================
    # WORKSPACE
    # ========================================================

    st.markdown(
        '<div class="dw-side-title">WORKSPACE</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.df is not None:

        st.markdown(
            f'<div class="dw-card"><b>{st.session_state.source_name}</b><br><span class="dw-muted">{len(st.session_state.df):,} rows · {len(st.session_state.df.columns)} columns</span></div>',
            unsafe_allow_html=True,
        )

    if st.button(
        "Clear chat history",
        width="stretch",
    ):
        st.session_state.chat = []
        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

head_left, head_right = st.columns([5, 2])

with head_left:

    st.markdown(
        '<div class="dw-main-brand"><div class="dw-home">⌂</div><div><div class="dw-main-title">Data Workspace</div><div class="dw-main-sub">Upload. Connect. Ask. Analyze. Visualize.</div></div></div>',
        unsafe_allow_html=True,
    )


with head_right:

    a, b = st.columns(2)

    with a:

        if st.button(
            "☀ / ◐",
            width="stretch",
        ):

            st.session_state.theme = (
                "light"
                if st.session_state.theme == "dark"
                else "dark"
            )

            st.rerun()

    with b:

        st.markdown(
            '<div class="dw-status"><span class="dw-dot"></span>Ready to analyze</div>',
            unsafe_allow_html=True,
        )


st.markdown(
    "<div style='height:14px'></div>",
    unsafe_allow_html=True,
)


# ============================================================
# EMPTY STATE
# ============================================================

if st.session_state.df is None:

    st.markdown(
        '<div class="dw-empty"><div><div style="font-size:32px;color:var(--accent)">✦</div><h2>Bring your data in</h2><p>Choose CSV, Excel, JSON, PDF tables, SQLite or PostgreSQL from the left.</p><div style="color:var(--muted);font-size:10px">CSV · Excel · JSON · PDF tables · SQLite · PostgreSQL</div></div></div>',
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# DATASET
# ============================================================

df = st.session_state.df


# ============================================================
# SOURCE BANNER
# ============================================================

safe_source_name = (
    st.session_state.source_name
    .replace("<", "&lt;")
    .replace(">", "&gt;")
)

st.markdown(
    f'<div class="dw-card dw-source-banner"><div class="dw-source-icon">▤</div><div style="flex:1"><div class="dw-source-title">{safe_source_name} <span class="dw-connected">Connected</span></div><div class="dw-source-sub">Table/data loaded successfully · {len(df):,} rows · {len(df.columns)} columns</div></div></div>',
    unsafe_allow_html=True,
)


# ============================================================
# DATASET PREVIEW + INFORMATION
# ============================================================

left, right = st.columns(
    [3.2, 1.05],
    gap="medium",
)


with left:

    st.markdown(
        '<div class="dw-card-title">▦ Dataset Preview <small>First 10 rows</small></div>',
        unsafe_allow_html=True,
    )

    st.dataframe(
        df,
        width="stretch",
        height=300,
        hide_index=True,
    )


with right:

    missing = int(
        df.isna().sum().sum()
    )

    dup = int(
        df.duplicated().sum()
    )

    with st.container(border=True):

        st.markdown(
            '<div class="dw-card-title">▥ Dataset Information</div>',
            unsafe_allow_html=True,
        )

        for k, v in [
            ("Rows", f"{len(df):,}"),
            ("Columns", len(df.columns)),
            ("Missing values", missing),
            ("Duplicate rows", dup),
        ]:

            st.markdown(
                f'<div class="dw-info-row"><span>{k}</span><strong>{v}</strong></div>',
                unsafe_allow_html=True,
            )


    quality = max(
        0,
        round(
            100
            * (
                1
                - (
                    missing
                    / max(
                        1,
                        len(df) * len(df.columns),
                    )
                )
                - (
                    dup
                    / max(1, len(df))
                    * 0.15
                )
            )
        ),
    )

    with st.container(border=True):

        st.markdown(
            f'<div class="dw-quality"><div class="dw-ring">{quality}%</div><div><div class="dw-good">Good</div><div class="dw-muted">Dataset quality score</div></div></div>',
            unsafe_allow_html=True,
        )


    with st.container(border=True):

        st.markdown(
            '<div class="dw-card-title">▱ Column types</div>',
            unsafe_allow_html=True,
        )

        numeric = int(
            sum(
                pd.api.types.is_numeric_dtype(x)
                for x in df.dtypes
            )
        )

        date = int(
            sum(
                pd.api.types.is_datetime64_any_dtype(x)
                for x in df.dtypes
            )
        )

        text = (
            len(df.columns)
            - numeric
            - date
        )

        for k, v in [
            ("Numeric", numeric),
            ("Categorical / text", text),
            ("Date / time", date),
        ]:

            st.markdown(
                f'<div class="dw-type-row"><span>| {k}</span><b>{v}</b></div>',
                unsafe_allow_html=True,
            )


# ============================================================
# ASK DATA
# ============================================================

st.markdown(
    '<div class="dw-question-title">✦ Ask a question about your data</div>',
    unsafe_allow_html=True,
)


with st.form(
    "data_question_form",
    clear_on_submit=True,
):

    input_col, button_col = st.columns(
        [8, 1]
    )

    with input_col:

        question = st.text_input(
            "Question",
            placeholder="e.g. Which city has the most customers?",
            label_visibility="collapsed",
        )

    with button_col:

        submitted = st.form_submit_button(
            "➤",
            type="primary",
            width="stretch",
        )


# ============================================================
# AI ANALYSIS
# ============================================================

if submitted and question.strip():

    question = question.strip()

    # Save user question

    st.session_state.chat.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.spinner(
        "DataWhisperer is analyzing your data..."
    ):

        try:

            # ------------------------------------------------
            # STEP 1 — Generate Pandas code
            # ------------------------------------------------

            code = generate_code(
                question,
                dataset_context(df),
                provider_key,
            )


            # ------------------------------------------------
            # STEP 2 — Execute generated code
            # ------------------------------------------------

            result = execute_analysis_code(
                code,
                df,
            )


            # ------------------------------------------------
            # STEP 3 — Handle execution result
            # ------------------------------------------------

            if result["error"]:

                answer = (
                    "I couldn't safely execute "
                    "the generated analysis.\n\n"
                    f"{result['error']}"
                )

            else:

                value = result["result"]


                # ============================================
                # Prepare result for AI explanation
                # ============================================

                if isinstance(
                    value,
                    pd.DataFrame,
                ):

                    explanation_data = (
                        value
                        .head(100)
                        .to_markdown(
                            index=False
                        )
                    )

                elif isinstance(
                    value,
                    pd.Series,
                ):

                    explanation_data = (
                        value
                        .rename(
                            value.name or "Value"
                        )
                        .reset_index()
                        .head(100)
                        .to_markdown(
                            index=False
                        )
                    )

                else:

                    explanation_data = str(
                        value
                    )


                # ============================================
                # STEP 4 — AI explains actual result
                # ============================================

                answer = explain_result(
                    question,
                    explanation_data,
                    provider_key,
                )


            # ------------------------------------------------
            # STEP 5 — Save complete response
            # ------------------------------------------------

            st.session_state.chat.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "code": code,
                    "figure": result.get("figure"),
                    "raw_result": result.get("result"),
                }
            )


        except Exception as e:

            st.session_state.chat.append(
                {
                    "role": "assistant",
                    "content": (
                        f"AI analysis failed: {e}"
                    ),
                }
            )

    st.rerun()


# ============================================================
# CHAT HISTORY
# ============================================================

for msg in st.session_state.chat:

    with st.chat_message(
        msg["role"]
    ):

        # ====================================================
        # USER
        # ====================================================

        if msg["role"] == "user":

            st.write(
                msg["content"]
            )


        # ====================================================
        # ASSISTANT
        # ====================================================

        else:

            # ------------------------------------------------
            # AI ANSWER
            # ------------------------------------------------

            st.markdown(
                msg["content"]
            )


            # ------------------------------------------------
            # ACTUAL RESULT TABLE
            # ------------------------------------------------

            raw_result = msg.get(
                "raw_result"
            )

            if isinstance(
                raw_result,
                pd.DataFrame,
            ):

                st.dataframe(
                    raw_result.head(100),
                    width="stretch",
                    hide_index=True,
                )


            elif isinstance(
                raw_result,
                pd.Series,
            ):

                display_result = (
                    raw_result
                    .rename(
                        raw_result.name or "Value"
                    )
                    .reset_index()
                )

                st.dataframe(
                    display_result.head(100),
                    width="stretch",
                    hide_index=True,
                )


            # ------------------------------------------------
            # CHART
            # ------------------------------------------------

            if msg.get("figure") is not None:

                st.pyplot(
                    msg["figure"],
                    clear_figure=False,
                    width="stretch",
                )


            # ------------------------------------------------
            # GENERATED CODE
            # ------------------------------------------------

            if msg.get("code"):

                with st.expander(
                    "Generated analysis code"
                ):

                    st.code(
                        msg["code"],
                        language="python",
                    )


# ============================================================
# QUESTION SUGGESTIONS
# ============================================================

if (
    df is not None
    and not st.session_state.chat
):

    suggestions = [
        "Total customers by city",
        "Show unique cities",
        "Count by city",
        "Show email domains",
    ]

    cols = st.columns(
        len(suggestions)
    )

    for col, text in zip(
        cols,
        suggestions,
    ):

        with col:

            st.markdown(
                f'<div class="dw-card" style="padding:8px 10px;text-align:center;font-size:9px;color:var(--muted)">↗ {text}</div>',
                unsafe_allow_html=True,
            )