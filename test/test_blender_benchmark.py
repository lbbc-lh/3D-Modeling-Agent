# -*- coding: utf-8 -*-

import json
from pathlib import Path
import unittest

from blender_agent.planner import build_blender_actions, is_blender_request
from function_call.slot_process import normalize_blender_action


class BlenderParsingTest(unittest.TestCase):
    def test_normalize_color_material_action(self):
        payload = {
            "function": [
                {
                    "function": {
                        "name": "apply_material",
                        "arguments": "{\"target\":\"Cube\",\"color\":\"red\"}",
                    }
                }
            ]
        }
        result = normalize_blender_action(payload)
        self.assertEqual(result["action"], "apply_material")
        self.assertEqual(result["params"]["color"], "red")


class BlenderBenchmarkTest(unittest.TestCase):
    def test_benchmark_dataset(self):
        dataset_path = Path("test/data/blender_benchmark.json")
        dataset = json.loads(dataset_path.read_text(encoding="utf-8"))

        accepted_total = 0
        accepted_correct = 0
        action_correct = 0

        for item in dataset:
            accepted = is_blender_request(item["query"])
            actions = build_blender_actions(item["query"])
            action_names = [action["action"] for action in actions]

            accepted_total += 1
            if accepted == item["accepted"]:
                accepted_correct += 1
            if action_names == item["expected_actions"]:
                action_correct += 1

        print(
            f"benchmark accepted={accepted_correct}/{accepted_total} "
            f"action_match={action_correct}/{accepted_total}"
        )

        self.assertEqual(accepted_correct, accepted_total)
        self.assertEqual(action_correct, accepted_total)


if __name__ == "__main__":
    unittest.main()
