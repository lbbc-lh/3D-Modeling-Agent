# -*- coding: utf-8 -*-

import unittest

from blender_agent.actions import execute_action
from blender_agent.executor import execute_actions
from mcp_core.blender_server import call_tool


class BlenderServerTest(unittest.TestCase):
    def test_unknown_tool_returns_error(self):
        result = call_tool("unknown_action", {})
        self.assertFalse(result["success"])
        self.assertIn("unsupported", result["error"])


class BlenderExecutionTest(unittest.TestCase):
    def test_create_primitive_returns_success_payload(self):
        result = execute_action({"action": "create_primitive", "params": {"primitive": "cube"}})
        self.assertIn("success", result)
        self.assertIn("action", result)
        self.assertIn("artifacts", result)
        self.assertIn("error", result)

    def test_execute_actions_accumulates_results(self):
        result = execute_actions(
            [
                {"action": "create_primitive", "params": {"primitive": "cube"}},
                {"action": "render_scene", "params": {"output_path": "outputs/test.png"}},
            ]
        )
        self.assertEqual(result["executed_actions"], 2)
        self.assertIn("success", result)
        self.assertIn("results", result)
        self.assertIn("errors", result)
        self.assertIn("mode", result)


if __name__ == "__main__":
    unittest.main()
