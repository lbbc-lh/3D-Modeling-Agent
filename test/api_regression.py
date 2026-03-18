# -*- coding: utf-8 -*-

import os
import uuid
import unittest

import requests


INTENT_URL = os.getenv("INTENT_URL", "http://127.0.0.1:8008/intent-server/v1")
REJECT_URL = os.getenv("REJECT_URL", "http://127.0.0.1:8007/reject-server/v1")
NLU_URL = os.getenv("NLU_URL", "http://127.0.0.1:8009/chatnlu-server/v1")

INTENT_HEALTH = os.getenv("INTENT_HEALTH", "http://127.0.0.1:8008/health")
REJECT_HEALTH = os.getenv("REJECT_HEALTH", "http://127.0.0.1:8007/health")
NLU_HEALTH = os.getenv("NLU_HEALTH", "http://127.0.0.1:8009/health")
ENTRY_HEALTH = os.getenv("ENTRY_HEALTH", "http://127.0.0.1:8080/health")


class ApiRegressionTest(unittest.TestCase):
    def test_health(self):
        for url in [INTENT_HEALTH, REJECT_HEALTH, NLU_HEALTH, ENTRY_HEALTH]:
            res = requests.get(url, timeout=5)
            self.assertEqual(res.status_code, 200)

    def test_intent_happy_path(self):
        payload = {"query": "帮我打开空调", "trace_id": str(uuid.uuid4())}
        res = requests.post(INTENT_URL, json=payload, timeout=10)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("data", data)
        self.assertIn("score", data)

    def test_reject_happy_path(self):
        payload = {"query": "今天天气如何", "thres": 0.5, "trace_id": str(uuid.uuid4())}
        res = requests.post(REJECT_URL, json=payload, timeout=10)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("data", data)
        self.assertIn("score", data)

    def test_nlu_bad_payload(self):
        payload = {"query": None, "trace_id": str(uuid.uuid4())}
        res = requests.post(NLU_URL, json=payload, timeout=10)
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertIn("intent", data)


if __name__ == "__main__":
    unittest.main()
