"""
Result Store — thread-safe in-memory store for pipeline results.
Acts as a lightweight job registry keyed by job_id.
"""
from __future__ import annotations

import threading
from typing import Any, Dict, Optional

_store: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()


def save(job_id: str, data: Dict[str, Any]) -> None:
    with _lock:
        _store[job_id] = data


def get(job_id: str) -> Optional[Dict[str, Any]]:
    with _lock:
        return _store.get(job_id)


def update(job_id: str, patch: Dict[str, Any]) -> None:
    with _lock:
        if job_id in _store:
            _store[job_id].update(patch)


def delete(job_id: str) -> None:
    with _lock:
        _store.pop(job_id, None)


def all_jobs() -> Dict[str, Dict[str, Any]]:
    with _lock:
        return dict(_store)
