from __future__ import annotations

import ast
import builtins
import io
import math
import traceback
from contextlib import redirect_stderr, redirect_stdout

import matplotlib.pyplot as plt
import pandas as pd


BLOCKED_NODES = (
    ast.Import, ast.ImportFrom, ast.FunctionDef, ast.AsyncFunctionDef,
    ast.ClassDef, ast.Lambda, ast.With, ast.AsyncWith, ast.Try, ast.Raise,
    ast.Delete, ast.Global, ast.Nonlocal, ast.While, ast.Yield, ast.YieldFrom,
)
BLOCKED_CALLS = {"eval", "exec", "compile", "open", "input", "__import__", "breakpoint"}


def validate_code(code: str) -> None:
    tree = ast.parse(code, mode="exec")
    for node in ast.walk(tree):
        if isinstance(node, BLOCKED_NODES):
            raise ValueError(f"Blocked Python construct: {type(node).__name__}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in BLOCKED_CALLS:
            raise ValueError(f"Blocked function: {node.func.id}")
        if isinstance(node, ast.Attribute) and node.attr.startswith("__"):
            raise ValueError("Dunder attribute access is not allowed.")


def execute_analysis_code(code: str, df: pd.DataFrame):
    validate_code(code)
    plt.close("all")
    safe_builtins = {
        "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict,
        "enumerate": enumerate, "float": float, "int": int, "len": len,
        "list": list, "max": max, "min": min, "round": round, "set": set,
        "sorted": sorted, "str": str, "sum": sum, "tuple": tuple, "zip": zip,
    }
    env = {"df": df.copy(), "pd": pd, "math": math, "plt": plt, "__builtins__": safe_builtins}
    stdout = io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stdout):
            exec(compile(ast.parse(code, mode="exec"), "<analysis>", "exec"), env, env)
        result = env.get("result")
        if result is None and "answer" in env:
            result = env["answer"]
        if result is None:
            result = stdout.getvalue().strip()
        figure = plt.gcf() if plt.get_fignums() else None
        if figure is not None and not figure.axes:
            figure = None
        return {"result": result, "figure": figure, "stdout": stdout.getvalue().strip(), "error": None}
    except Exception as exc:
        return {"result": None, "figure": None, "stdout": stdout.getvalue().strip(), "error": f"{type(exc).__name__}: {exc}"}


def dataset_context(df: pd.DataFrame) -> str:
    lines = [f"Rows: {len(df)}", f"Columns: {len(df.columns)}"]
    for col in df.columns:
        sample = df[col].dropna().astype(str).head(3).tolist()
        lines.append(f"- {col}: dtype={df[col].dtype}, sample={sample}")
    return "\n".join(lines)
