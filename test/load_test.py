# -*- coding: utf-8 -*-

import argparse
import statistics
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


def one_request(url: str):
    start = time.time()
    try:
        res = requests.get(url, timeout=5)
        latency = (time.time() - start) * 1000
        return res.status_code, latency
    except Exception:
        latency = (time.time() - start) * 1000
        return 0, latency


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8080/health")
    parser.add_argument("--total", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=20)
    args = parser.parse_args()

    latencies = []
    ok = 0

    with ThreadPoolExecutor(max_workers=args.concurrency) as executor:
        futures = [executor.submit(one_request, args.url) for _ in range(args.total)]
        for f in as_completed(futures):
            code, latency = f.result()
            latencies.append(latency)
            if code == 200:
                ok += 1

    latencies.sort()
    p95 = latencies[int(len(latencies) * 0.95) - 1] if latencies else 0
    avg = statistics.mean(latencies) if latencies else 0
    fail = args.total - ok

    print("total:", args.total)
    print("success:", ok)
    print("failed:", fail)
    print("success_rate:", round(ok / args.total, 4))
    print("avg_ms:", round(avg, 2))
    print("p95_ms:", round(p95, 2))


if __name__ == "__main__":
    main()
