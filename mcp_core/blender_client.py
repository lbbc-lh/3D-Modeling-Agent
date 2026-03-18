# -*- coding: utf-8 -*-

from mcp_core.blender_server import call_tool


class BlenderMCPClient:
    def call_tool(self, action_name, params):
        return call_tool(action_name, params)
