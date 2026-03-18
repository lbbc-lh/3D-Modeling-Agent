# Blender Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local Blender-oriented agent MVP in `/Users/hedyliang/Desktop/blender_agent` that turns natural-language requests into validated Blender actions, executes them through a local MCP-style bridge, and returns structured results.

**Architecture:** Reuse the copied project entry and function-calling skeleton, but narrow the runtime to a Blender-first flow. Add a new `blender_agent/` package for action models, validation, and execution, and add `mcp_core/blender_client.py` plus `mcp_core/blender_server.py` as a thin MCP-style bridge over local Blender Python execution.

**Tech Stack:** Python, Flask-SocketIO, FastAPI, requests, local JSON schema-like validation, Blender Python API (`bpy`) via background execution, unittest

---

## File Structure

- Modify: `start.py`
  - route requests into Blender-specific parse and execute flow
- Modify: `function_call/function.py`
  - define only the 5 Blender tool schemas for MVP
- Modify: `function_call/chatnlu_infer.py`
  - parse Blender actions instead of old broad domain actions
- Modify: `function_call/slot_process.py`
  - normalize Blender parameters and action payloads
- Create: `blender_agent/__init__.py`
- Create: `blender_agent/models.py`
  - define action and execution result helpers
- Create: `blender_agent/validators.py`
  - validate required params and supported values
- Create: `blender_agent/actions.py`
  - dispatch validated actions by name
- Create: `blender_agent/executor.py`
  - run 1 to 3 actions in sequence and accumulate results
- Create: `blender_agent/blender_bridge.py`
  - detect Blender, run background scripts, normalize outputs
- Create: `blender_agent/bpy_runner.py`
  - actual `bpy` calls for primitive creation, transforms, materials, camera/light setup, render
- Create: `mcp_core/blender_client.py`
  - local wrapper for `call_tool`
- Create: `mcp_core/blender_server.py`
  - map tool names to action handlers
- Create: `test/test_blender_validators.py`
- Create: `test/test_blender_executor.py`
- Create: `test/test_blender_benchmark.py`
- Create: `test/data/blender_benchmark.json`
- Optionally modify: `README.md`
  - document Blender MVP run flow if needed after implementation

### Task 1: Establish Blender Domain Models and Validation

**Files:**
- Create: `blender_agent/__init__.py`
- Create: `blender_agent/models.py`
- Create: `blender_agent/validators.py`
- Test: `test/test_blender_validators.py`

- [ ] **Step 1: Write the failing validator tests**

```python
import unittest

from blender_agent.validators import validate_action


class BlenderValidatorTest(unittest.TestCase):
    def test_create_primitive_requires_supported_primitive(self):
        ok, error = validate_action({"action": "create_primitive", "params": {"primitive": "cube"}})
        self.assertTrue(ok)
        self.assertEqual(error, "")

    def test_apply_material_requires_target_and_color(self):
        ok, error = validate_action({"action": "apply_material", "params": {"target": "Cube"}})
        self.assertFalse(ok)
        self.assertIn("color", error)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test/test_blender_validators.py -v`
Expected: FAIL with `ModuleNotFoundError` or missing `validate_action`

- [ ] **Step 3: Write minimal implementation**

```python
SUPPORTED_ACTIONS = {
    "create_primitive": {"required": ["primitive"]},
    "transform_object": {"required": ["target"]},
    "apply_material": {"required": ["target", "color"]},
    "setup_camera_light": {"required": []},
    "render_scene": {"required": []},
}


def validate_action(action_payload):
    action_name = action_payload.get("action")
    params = action_payload.get("params", {})
    if action_name not in SUPPORTED_ACTIONS:
        return False, f"unsupported action: {action_name}"
    for key in SUPPORTED_ACTIONS[action_name]["required"]:
        if key not in params or params[key] in ("", None):
            return False, f"missing required param: {key}"
    if action_name == "create_primitive" and params.get("primitive") not in {"cube", "sphere", "plane"}:
        return False, "unsupported primitive"
    return True, ""
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test/test_blender_validators.py -v`
Expected: PASS

- [ ] **Step 5: Review checkpoint**

Review:
- confirm action names exactly match the spec
- confirm validation errors are structured enough to surface to entry layer
- confirm no Blender runtime dependency is introduced yet

- [ ] **Step 6: Commit**

```bash
git add blender_agent/__init__.py blender_agent/models.py blender_agent/validators.py test/test_blender_validators.py
git commit -m "feat: add blender action models and validators"
```

Current environment note: `/Users/hedyliang/Desktop/blender_agent` is not a Git repository yet, so treat this as a deferred step unless the repo is initialized later.

### Task 2: Add Local MCP-Style Blender Bridge

**Files:**
- Create: `mcp_core/blender_client.py`
- Create: `mcp_core/blender_server.py`
- Create: `blender_agent/actions.py`
- Test: `test/test_blender_executor.py`

- [ ] **Step 1: Write the failing bridge test**

```python
import unittest

from mcp_core.blender_server import call_tool


class BlenderServerTest(unittest.TestCase):
    def test_unknown_tool_returns_error(self):
        result = call_tool("unknown_action", {})
        self.assertFalse(result["success"])
        self.assertIn("unsupported", result["error"])
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: FAIL with import error or missing `call_tool`

- [ ] **Step 3: Write minimal implementation**

```python
from blender_agent.validators import validate_action


def call_tool(action_name, params):
    payload = {"action": action_name, "params": params}
    ok, error = validate_action(payload)
    if not ok:
        return {"success": False, "error": error}
    return {"success": True, "action": payload}
```

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: PASS

- [ ] **Step 5: Review checkpoint**

Review:
- confirm `mcp_core/blender_client.py` only wraps the server contract
- confirm tool names still match the 5 MVP actions
- confirm the bridge stays local-first and does not add unnecessary protocol complexity

- [ ] **Step 6: Commit**

```bash
git add mcp_core/blender_client.py mcp_core/blender_server.py blender_agent/actions.py test/test_blender_executor.py
git commit -m "feat: add local blender mcp bridge"
```

Current environment note: skip this until the project is initialized as a Git repository.

### Task 3: Implement Blender Background Execution Layer

**Files:**
- Create: `blender_agent/blender_bridge.py`
- Create: `blender_agent/bpy_runner.py`
- Modify: `blender_agent/actions.py`
- Modify: `test/test_blender_executor.py`

- [ ] **Step 1: Write the failing execution test**

```python
import unittest

from blender_agent.actions import execute_action


class BlenderExecutionTest(unittest.TestCase):
    def test_create_primitive_returns_success_payload(self):
        result = execute_action({"action": "create_primitive", "params": {"primitive": "cube"}})
        self.assertIn("success", result)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: FAIL with missing `execute_action`

- [ ] **Step 3: Write minimal implementation**

```python
def execute_action(action_payload):
    return {
        "success": True,
        "action": action_payload["action"],
        "artifacts": {},
        "error": "",
    }
```

Then extend it to:
- detect Blender binary from env such as `BLENDER_BIN`
- provide a dry-run fallback when Blender is unavailable
- route to `bpy_runner.py` for real execution

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: PASS

- [ ] **Step 5: Review checkpoint**

Review:
- confirm Blender detection happens before long execution
- confirm errors are normalized into response payloads
- confirm render outputs are planned under a deterministic directory like `outputs/`

- [ ] **Step 6: Commit**

```bash
git add blender_agent/blender_bridge.py blender_agent/bpy_runner.py blender_agent/actions.py test/test_blender_executor.py
git commit -m "feat: add blender execution bridge"
```

Current environment note: skip this until the project is initialized as a Git repository.

### Task 4: Replace Old Tool Schema With Blender Tool Parsing

**Files:**
- Modify: `function_call/function.py`
- Modify: `function_call/chatnlu_infer.py`
- Modify: `function_call/slot_process.py`
- Test: `test/test_blender_benchmark.py`
- Test data: `test/data/blender_benchmark.json`

- [ ] **Step 1: Write the failing parsing test**

```python
import unittest

from function_call.slot_process import normalize_blender_action


class BlenderParsingTest(unittest.TestCase):
    def test_normalize_color_material_action(self):
        payload = {"function": [{"function": {"name": "apply_material", "arguments": "{\"target\":\"Cube\",\"color\":\"red\"}"}}]}
        result = normalize_blender_action(payload)
        self.assertEqual(result["action"], "apply_material")
        self.assertEqual(result["params"]["color"], "red")
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test/test_blender_benchmark.py -v`
Expected: FAIL with missing `normalize_blender_action`

- [ ] **Step 3: Write minimal implementation**

```python
def normalize_blender_action(tool_calls):
    function_call = tool_calls["function"][0]["function"]
    return {
        "action": function_call["name"],
        "params": json.loads(function_call["arguments"]),
    }
```

Then extend it to:
- normalize primitive aliases
- normalize RGB or color names
- preserve only supported params

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test/test_blender_benchmark.py -v`
Expected: PASS

- [ ] **Step 5: Review checkpoint**

Review:
- confirm only 5 Blender tools remain exposed to the LLM
- confirm action payloads from parsing match validator expectations exactly
- confirm old unrelated domains do not leak into the Blender path

- [ ] **Step 6: Commit**

```bash
git add function_call/function.py function_call/chatnlu_infer.py function_call/slot_process.py test/test_blender_benchmark.py test/data/blender_benchmark.json
git commit -m "feat: add blender tool parsing flow"
```

Current environment note: skip this until the project is initialized as a Git repository.

### Task 5: Route Entry Requests Into Blender Intent, Reject, and Execution

**Files:**
- Modify: `start.py`
- Create or Modify: `blender_agent/executor.py`
- Modify: `blender_agent/models.py`
- Modify: `test/test_blender_executor.py`

- [ ] **Step 1: Write the failing entry-flow test**

```python
import unittest

from blender_agent.executor import execute_actions


class BlenderExecutorFlowTest(unittest.TestCase):
    def test_execute_actions_accumulates_results(self):
        result = execute_actions([
            {"action": "create_primitive", "params": {"primitive": "cube"}},
            {"action": "render_scene", "params": {"output_path": "outputs/test.png"}},
        ])
        self.assertEqual(result["executed_actions"], 2)
```

- [ ] **Step 2: Run test to verify it fails**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: FAIL with missing `execute_actions`

- [ ] **Step 3: Write minimal implementation**

```python
def execute_actions(actions):
    results = []
    for action in actions:
        results.append(execute_action(action))
    return {
        "success": all(item["success"] for item in results),
        "executed_actions": len(results),
        "results": results,
        "errors": [item["error"] for item in results if item["error"]],
    }
```

Then update `start.py` to:
- bypass broad chat fallback for Blender MVP requests
- call Blender parse and validation path
- return structured rejection for unrelated queries
- return structured execution payload on success

- [ ] **Step 4: Run test to verify it passes**

Run: `python -m unittest test/test_blender_executor.py -v`
Expected: PASS

- [ ] **Step 5: Review checkpoint**

Review:
- confirm entry payload shape still includes `query` and `trace_id`
- confirm unrelated requests do not try to execute Blender
- confirm the response envelope matches the spec

- [ ] **Step 6: Commit**

```bash
git add start.py blender_agent/executor.py blender_agent/models.py test/test_blender_executor.py
git commit -m "feat: wire blender entry execution flow"
```

Current environment note: skip this until the project is initialized as a Git repository.

### Task 6: Add Benchmark Dataset and Final Verification

**Files:**
- Create or Modify: `test/data/blender_benchmark.json`
- Modify: `test/test_blender_benchmark.py`
- Optionally Modify: `README.md`

- [ ] **Step 1: Write the benchmark dataset**

```json
[
  {
    "query": "创建一个红色立方体并渲染",
    "accepted": true,
    "expected_actions": ["create_primitive", "apply_material", "render_scene"]
  },
  {
    "query": "今天天气怎么样",
    "accepted": false,
    "expected_actions": []
  }
]
```

- [ ] **Step 2: Add the benchmark test runner**

Run logic:
- load benchmark dataset
- run intent/reject and parsing path
- compare accepted flag
- compare expected action names
- print simple summary counts

- [ ] **Step 3: Run full test suite**

Run: `python -m unittest test/test_blender_validators.py test/test_blender_executor.py test/test_blender_benchmark.py -v`
Expected: PASS

- [ ] **Step 4: Run targeted manual verification**

Run:
- `python -m unittest test/test_blender_benchmark.py -v`
- optional entry smoke test if environment is ready

Expected:
- benchmark summary prints acceptance and action-match counts
- no unexpected import or runtime errors

- [ ] **Step 5: Review checkpoint**

Review:
- confirm benchmark reflects both positive and negative cases
- confirm at least one path covers render output artifact expectations
- confirm README only documents what actually runs locally

- [ ] **Step 6: Commit**

```bash
git add test/data/blender_benchmark.json test/test_blender_benchmark.py README.md
git commit -m "test: add blender benchmark coverage"
```

Current environment note: skip this until the project is initialized as a Git repository.

## Execution Notes

- Keep each task reviewable before moving on
- Prefer minimal passing implementations first, then extend
- If local Blender is unavailable, keep dry-run coverage and surface the missing binary clearly
- Do not touch `/Users/hedyliang/Desktop/项目源码`; all changes stay in `/Users/hedyliang/Desktop/blender_agent`

## Verification Commands

- `python -m unittest test/test_blender_validators.py -v`
- `python -m unittest test/test_blender_executor.py -v`
- `python -m unittest test/test_blender_benchmark.py -v`
- `python -m unittest test/test_blender_validators.py test/test_blender_executor.py test/test_blender_benchmark.py -v`
