from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Dict, Iterable, Optional, Union

import yaml


def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in b.items():
        if k in out and isinstance(out[k], dict) and isinstance(v, dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _expand_env(value: Any) -> Any:
    """
    Recursively expand environment variables in strings using ${VAR} or $VAR syntax.
    """
    if isinstance(value, str):
        return os.path.expandvars(value)
    if isinstance(value, dict):
        return {k: _expand_env(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_expand_env(v) for v in value]
    return value


def load_config(paths: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    """
    Load and merge YAML configs from a list of paths (later files override earlier ones).
    Default search: ["config/default.yaml"] if not provided.
    After load, expands environment variables present in string values.
    """
    paths = list(paths) if paths else ["config/default.yaml"]
    merged: Dict[str, Any] = {}
    for p in paths:
        path = Path(p)
        if not path.exists():
            continue
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        if not isinstance(data, dict):
            continue
        merged = _deep_merge(merged, data)
    return _expand_env(merged)


def get_openrouter_cfg(cfg: Dict[str, Any]) -> Dict[str, Any]:
    """
    Returns the llm.openrouter config sub-tree or an empty dict.
    """
    llm = cfg.get("llm") or {}
    if not isinstance(llm, dict):
        return {}
    openrouter = llm.get("openrouter") or {}
    return openrouter if isinstance(openrouter, dict) else {}