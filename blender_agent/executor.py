# -*- coding: utf-8 -*-

from blender_agent.actions import execute_action
from blender_agent.blender_bridge import run_blender_actions


def execute_actions(actions):
    batch_result = run_blender_actions(actions)
    if batch_result.get("mode") == "blender" or batch_result.get("mode") == "dry_run":
        return batch_result

    results = []
    errors = []

    for action in actions:
        result = execute_action(action)
        results.append(result)
        if result.get("error"):
            errors.append(result["error"])

    return {
        "success": all(item["success"] for item in results) if results else False,
        "executed_actions": len(results),
        "results": results,
        "errors": errors,
    }
