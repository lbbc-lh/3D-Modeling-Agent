# -*- coding: utf-8 -*-

import json
import time
import uuid
from typing import Dict, Optional

from utils import logger


def now_ms() -> int:
    return int(time.time() * 1000)


def ensure_trace_id(trace_id: Optional[str]) -> str:
    if trace_id:
        return str(trace_id)
    return uuid.uuid4().hex


def build_event(
    service: str,
    trace_id: str,
    latency_ms: int,
    status: str,
    **fields: Dict[str, str],
) -> str:
    payload = {
        "trace_id": trace_id,
        "service": service,
        "latency_ms": latency_ms,
        "status": status,
    }
    payload.update(fields)
    return json.dumps(payload, ensure_ascii=False)


def log_event(service: str, trace_id: str, latency_ms: int, status: str, **fields):
    logger.info(build_event(service, trace_id, latency_ms, status, **fields))
