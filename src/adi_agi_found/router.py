from __future__ import annotations
from typing import Dict, Any
from .config import Settings

def alias_map(s: Settings) -> Dict[str, str]:
    return {
        s.alias_7b: s.model_id_7b,
        s.alias_30b: s.model_id_30b,
        s.alias_70b: s.model_id_70b,
        s.alias_auto: s.model_id_7b,
        s.alias_mm: s.model_id_7b,
        s.alias_swarm: s.model_id_7b,
    }

def resolve_backend_model(s: Settings, alias: str, mapping: Dict[str, str], body: Dict[str, Any], route_hint: str | None) -> str:
    if alias == s.alias_auto:
        msgs = body.get("messages") or []
        text = ""
        for m in msgs:
            c = m.get("content")
            if isinstance(c, str):
                text += c
        hint = (route_hint or "").lower()
        if hint == "fast":
            return mapping[s.alias_7b]
        if hint == "deep":
            return mapping[s.alias_70b]
        return mapping[s.alias_7b] if len(text) <= s.auto_threshold_chars else mapping[s.alias_70b]
    hint = (route_hint or "").lower()
    if hint == "fast":
        return mapping[s.alias_7b]
    if hint == "deep":
        return mapping[s.alias_70b]
    return mapping[alias]
