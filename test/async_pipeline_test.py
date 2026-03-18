# -*- coding: utf-8 -*-

import json
import os
import time
import uuid

import requests


ENTRY_SOCKETIO_URL = os.getenv("ENTRY_URL", "http://127.0.0.1:8080")
ASYNC_LOG_FILE = os.getenv("ASYNC_LOG_FILE_LOCAL", "./log/async_tasks.log")


def run_once():
    # 用 /health 触发基础可用性检查，业务请求可通过 dialog.py 进行 socket 触发
    requests.get(f"{ENTRY_SOCKETIO_URL}/health", timeout=5)

    trace_id = str(uuid.uuid4())
    print(f"please run dialog.py and send one query with trace_id={trace_id}")

    start = time.time()
    while time.time() - start < 30:
        if not os.path.exists(ASYNC_LOG_FILE):
            time.sleep(1)
            continue
        with open(ASYNC_LOG_FILE, "r", encoding="utf-8") as fp:
            lines = fp.readlines()
        for line in reversed(lines[-200:]):
            payload = json.loads(line)
            task = payload.get("task", {})
            if task.get("trace_id") == trace_id:
                print("async consume success:", payload)
                return True
        time.sleep(1)

    print("async consume timeout")
    return False


if __name__ == "__main__":
    ok = run_once()
    raise SystemExit(0 if ok else 1)
