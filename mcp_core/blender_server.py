# -*- coding: utf-8 -*-

from blender_agent.actions import build_action_payload


def call_tool(action_name, params):
    result = build_action_payload(action_name, params)
    if not result["success"]:
        return {"success": False, "error": result["error"]}
    return {"success": True, "action": result["action"], "error": ""}

