# -*- coding: utf-8 -*-

from blender_agent.blender_bridge import run_blender_action
from blender_agent.validators import validate_action


def build_action_payload(action_name, params):
    payload = {"action": action_name, "params": params}
    ok, error = validate_action(payload)
    if not ok:
        return {"success": False, "error": error}
    return {"success": True, "action": payload, "error": ""}


def execute_action(action_payload):
    ok, error = validate_action(action_payload)
    if not ok:
        return {
            "success": False,
            "action": action_payload.get("action", ""),
            "artifacts": {},
            "error": error,
        }

    result = run_blender_action(action_payload)
    return {
        "success": result["success"],
        "action": action_payload["action"],
        "artifacts": result.get("artifacts", {}),
        "error": result.get("error", ""),
    }
