# -*- coding: utf-8 -*-

from blender_agent.models import SUPPORTED_ACTIONS, SUPPORTED_PRIMITIVES


def validate_action(action_payload):
    action_name = action_payload.get("action")
    params = action_payload.get("params", {})

    if action_name not in SUPPORTED_ACTIONS:
        return False, f"unsupported action: {action_name}"

    for key in SUPPORTED_ACTIONS[action_name]["required"]:
        if key not in params or params[key] in ("", None):
            return False, f"missing required param: {key}"

    if action_name == "create_primitive":
        if params.get("primitive") not in SUPPORTED_PRIMITIVES:
            return False, "unsupported primitive"

    return True, ""
