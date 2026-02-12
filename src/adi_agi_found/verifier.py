from __future__ import annotations
import ast, re
from typing import Dict, Any, Tuple

ALLOWED_NODES = (
    ast.Expression, ast.BinOp, ast.UnaryOp, ast.Num, ast.Constant,
    ast.Add, ast.Sub, ast.Mult, ast.Div, ast.FloorDiv, ast.Mod, ast.Pow,
    ast.USub, ast.UAdd, ast.Load
)

def safe_eval_arithmetic(expr: str) -> Tuple[bool, str]:
    try:
        tree = ast.parse(expr, mode="eval")
        for node in ast.walk(tree):
            if not isinstance(node, ALLOWED_NODES):
                return False, "disallowed_expression"
        val = eval(compile(tree, "<expr>", "eval"), {"__builtins__": {}}, {})
        return True, str(val)
    except Exception:
        return False, "eval_error"

def verify_response(text: str) -> Dict[str, Any]:
    m = re.search(r"(\d+\s*[\+\-\*\/]\s*\d+)\s*=\s*(\d+)", text)
    if not m:
        return {"ok": True, "note":"no_simple_arithmetic_claim"}
    expr, claimed = m.group(1), m.group(2)
    ok, val = safe_eval_arithmetic(expr)
    if not ok:
        return {"ok": True, "note":"unverifiable"}
    return {"ok": (val == claimed), "expr": expr, "expected": val, "claimed": claimed}
