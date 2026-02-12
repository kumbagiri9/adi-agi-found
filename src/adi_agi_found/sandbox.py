from __future__ import annotations
import ast, io, os, sys, traceback
from multiprocessing import get_context
from pathlib import Path
from typing import Any, Dict

_ALLOWED_MODULES = {
    "math": __import__("math"),
    "json": __import__("json"),
    "re": __import__("re"),
    "statistics": __import__("statistics"),
    "datetime": __import__("datetime"),
}

def _safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    top = str(name).split(".")[0]
    if top in _ALLOWED_MODULES:
        return _ALLOWED_MODULES[top]
    raise ImportError("import_not_allowed")

_ALLOWED_BUILTINS = {
    "abs": abs, "all": all, "any": any, "bool": bool, "dict": dict, "enumerate": enumerate,
    "float": float, "int": int, "len": len, "list": list, "max": max, "min": min,
    "print": print, "range": range, "round": round, "sorted": sorted, "str": str,
    "sum": sum, "tuple": tuple, "zip": zip,
    "__import__": _safe_import,
}

_DISALLOWED_NAMES = {
    "eval", "exec", "open", "compile", "input",
    "os", "sys", "subprocess", "socket", "pathlib", "shutil",
    "requests", "httpx", "urllib", "importlib",
}

class SandboxError(Exception):
    pass

def _validate_ast(code: str) -> None:
    try:
        tree = ast.parse(code, mode="exec")
    except SyntaxError as e:
        raise SandboxError(f"syntax_error: {e}")
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = []
            if isinstance(node, ast.Import):
                names = [a.name.split(".")[0] for a in node.names]
            else:
                if node.module:
                    names = [node.module.split(".")[0]]
            for n in names:
                if n not in _ALLOWED_MODULES:
                    raise SandboxError(f"import_not_allowed: {n}")
        if isinstance(node, ast.Attribute):
            # allow module.attr only for allowlisted modules; deny dunder attrs
            if isinstance(node.value, ast.Name) and node.value.id in _ALLOWED_MODULES and not str(node.attr).startswith("__"):
                continue
            raise SandboxError("attribute_access_not_allowed")
        if isinstance(node, (ast.With, ast.Try, ast.Raise, ast.Lambda, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            raise SandboxError("complex_construct_not_allowed")
        if isinstance(node, ast.Name) and node.id in _DISALLOWED_NAMES:
            raise SandboxError(f"name_not_allowed: {node.id}")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in _DISALLOWED_NAMES:
            raise SandboxError(f"call_not_allowed: {node.func.id}")

def _worker(code: str, workdir: str, q) -> None:
    try:
        Path(workdir).mkdir(parents=True, exist_ok=True)
        os.chdir(workdir)
        _validate_ast(code)

        stdout = io.StringIO()
        stderr = io.StringIO()
        old_out, old_err = sys.stdout, sys.stderr
        sys.stdout, sys.stderr = stdout, stderr

        g: Dict[str, Any] = {"__builtins__": _ALLOWED_BUILTINS}
        g.update(_ALLOWED_MODULES)

        tree = ast.parse(code, mode="exec")
        result = None
        if tree.body and isinstance(tree.body[-1], ast.Expr):
            last = tree.body.pop()
            exec(compile(tree, "<sandbox>", "exec"), g, g)
            result = eval(compile(ast.Expression(last.value), "<sandbox>", "eval"), g, g)
        else:
            exec(compile(tree, "<sandbox>", "exec"), g, g)

        sys.stdout, sys.stderr = old_out, old_err
        q.put({"ok": True, "stdout": stdout.getvalue()[-8000:], "stderr": stderr.getvalue()[-8000:], "result": result})
    except SandboxError as e:
        q.put({"ok": False, "error": str(e)})
    except Exception:
        q.put({"ok": False, "error": "runtime_error", "trace": traceback.format_exc()[-8000:]})

def run_python_sandbox(code: str, *, workdir: str, timeout_sec: float) -> Dict[str, Any]:
    import multiprocessing as _mp
    method = "fork" if "fork" in _mp.get_all_start_methods() else "spawn"
    ctx = get_context(method)
    q = ctx.Queue()
    p = ctx.Process(target=_worker, args=(code, workdir, q), daemon=True)
    p.start()
    p.join(timeout=timeout_sec)
    if p.is_alive():
        p.terminate()
        return {"ok": False, "error": "timeout"}
    if q.empty():
        return {"ok": False, "error": "no_result"}
    return q.get()
