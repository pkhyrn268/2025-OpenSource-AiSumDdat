from typing import Any, Dict, Tuple, Optional

from flask import jsonify


def success(message: str, data: Optional[Dict[str, Any]] = None, status: int = 200) -> Tuple[Any, int]:
    payload: Dict[str, Any] = {"status": status, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


def error(message: str, status: int = 400, data: Optional[Dict[str, Any]] = None) -> Tuple[Any, int]:
    payload: Dict[str, Any] = {"status": status, "message": message}
    if data is not None:
        payload["data"] = data
    return jsonify(payload), status


__all__ = ["success", "error"]


