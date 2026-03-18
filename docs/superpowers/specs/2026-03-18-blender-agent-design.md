# Blender Agent Design

**Date:** 2026-03-18
**Project Root:** `/Users/hedyliang/Desktop/blender_agent`
**Status:** Draft reviewed with user

## 1. Goal

Build a local MVP of a Blender-oriented agent assistant on top of the copied codebase without modifying the original project. The assistant should accept natural-language requests, recognize whether they are valid Blender modeling instructions, extract structured actions and parameters, execute them through a local Blender Python bridge, and return structured execution results.

This MVP is intentionally narrow. It exists to demonstrate the resume narrative of an `LLM + MCP + 3D modeling intelligent design assistant`, not to become a general-purpose chat agent.

## 2. Scope

### In Scope

- Keep all changes inside `/Users/hedyliang/Desktop/blender_agent`
- Reuse the existing agent-style entry and function-calling structure where it reduces implementation cost
- Add a Blender-specific execution layer
- Add an MCP-style bridge layer so the code structure clearly reflects `LLM + MCP + Blender`
- Support these 5 executable actions:
  - `create_primitive`
  - `transform_object`
  - `apply_material`
  - `setup_camera_light`
  - `render_scene`
- Support valid-request detection via intent recognition and invalid-request rejection
- Add a minimal benchmark and automated tests for intent recognition, parameter extraction, and execution

### Out of Scope

- Complex scene planning across many dependent objects
- Conversational memory beyond what is already lightweight in the current project
- Full production-grade MCP protocol support
- Advanced Blender features such as geometry nodes, rigging, UV editing, or animation
- Fine-tuning a new model in this iteration

## 3. Product Framing

The copied project currently behaves like a general multi-service task agent. The Blender MVP changes the focus from broad task routing to a constrained modeling workflow:

1. User sends a natural-language Blender request
2. System decides whether the request is a valid Blender modeling command
3. System extracts one or more structured Blender actions
4. System sends those actions through an MCP-style bridge
5. Bridge invokes local Blender Python execution
6. System returns structured results, including generated file paths or errors

This framing directly supports the resume claims around:

- natural language to modeling instructions
- intent recognition and rejection
- LLM plus MCP integration
- benchmark-driven evaluation

## 4. Recommended Architecture

The MVP should use a thin adaptation of the copied codebase rather than a rewrite.

### 4.1 Main Layers

- `entry layer`
  - Accept request input
  - Build response envelope
  - Route request into Blender-specific parsing and execution flow
- `intent/reject layer`
  - Decide whether the input belongs to Blender modeling
  - Reject clearly invalid or unrelated input
- `action parsing layer`
  - Convert natural language into one or more structured Blender actions
  - Reuse function-calling style design from the existing codebase
- `mcp bridge layer`
  - Represent Blender operations as MCP-style tool calls
  - Decouple parsing from execution
- `blender execution layer`
  - Translate validated actions into `bpy` operations
  - Save outputs and return execution metadata
- `benchmark/test layer`
  - Validate intent classification, rejection, slot extraction, and execution outputs

### 4.2 Proposed File Layout

- Modify `start.py`
  - simplify or bypass broad chat/task arbitration for the Blender MVP path
- Modify `function_call/function.py`
  - replace or isolate tool schema to the 5 Blender actions
- Modify `function_call/chatnlu_infer.py`
  - produce Blender action candidates and slots
- Modify `function_call/slot_process.py`
  - normalize extracted Blender parameters
- Create `blender_agent/__init__.py`
- Create `blender_agent/models.py`
  - request, action, and execution result models
- Create `blender_agent/validators.py`
  - validate action payloads before execution
- Create `blender_agent/actions.py`
  - dispatch to action handlers
- Create `blender_agent/executor.py`
  - orchestrate action execution order
- Create `blender_agent/blender_bridge.py`
  - local Blender invocation and scene setup helpers
- Create `blender_agent/bpy_runner.py`
  - actual `bpy` implementation helpers
- Create `mcp_core/blender_server.py`
  - MCP-style Blender tool server surface
- Create `mcp_core/blender_client.py`
  - local client wrapper used by the agent
- Create benchmark and test files under `test/`

This layout keeps Blender-specific code isolated while still demonstrating that the copied project has evolved into an `LLM + MCP` assistant.

## 5. Action Contract

The assistant should standardize all executable steps into a small action format.

### 5.1 Action Envelope

```json
{
  "action": "create_primitive",
  "params": {
    "primitive": "cube",
    "name": "Cube",
    "location": [0, 0, 0],
    "rotation": [0, 0, 0],
    "scale": [1, 1, 1]
  }
}
```

### 5.2 Supported Actions

#### `create_primitive`

Required parameters:

- `primitive`: one of `cube`, `sphere`, `plane`

Optional parameters:

- `name`
- `location`
- `rotation`
- `scale`

#### `transform_object`

Required parameters:

- `target`

Optional parameters:

- `location`
- `rotation`
- `scale`

#### `apply_material`

Required parameters:

- `target`
- `color`

Optional parameters:

- `material_name`

#### `setup_camera_light`

Optional parameters:

- `camera_location`
- `camera_rotation`
- `light_type`
- `light_location`
- `light_energy`

#### `render_scene`

Optional parameters:

- `output_path`
- `resolution_x`
- `resolution_y`
- `samples`

### 5.3 Execution Result Envelope

```json
{
  "query": "创建一个红色立方体并渲染",
  "trace_id": "trace-123",
  "intent": "Blender建模",
  "function": "render_scene",
  "actions": [
    {
      "action": "create_primitive",
      "params": {
        "primitive": "cube"
      }
    }
  ],
  "execution": {
    "success": true,
    "executed_actions": 1,
    "output_image": "outputs/render.png",
    "scene_file": "outputs/session.blend",
    "errors": []
  }
}
```

## 6. Request Flow

The Blender MVP should prefer a deterministic, narrow flow over the original broad routing logic.

1. Receive input request
2. Build base response object with `query` and `trace_id`
3. Run Blender intent/reject decision
4. If rejected, return structured rejection result
5. If accepted, parse actions using LLM function calling and slot normalization
6. Validate action list before execution
7. Send actions through `mcp_core/blender_client.py`
8. Execute actions through `mcp_core/blender_server.py` into Blender bridge code
9. Return structured success or failure result

For MVP stability, each request should execute at most 1 to 3 actions in a linear sequence.

## 7. Intent Recognition and Rejection

This layer should exist even if the first version uses simple heuristics or lightweight local inference.

### 7.1 Purpose

- Demonstrate the `intent recognition + rejection` capability described in the resume
- Keep unrelated requests from reaching Blender execution
- Provide measurable benchmark output

### 7.2 MVP Strategy

Use one of these approaches, in descending priority:

1. Reuse the existing lightweight intent/reject structure and adapt labels toward Blender
2. Implement a temporary rules-plus-keywords fallback if model files or labels are too coupled to the old domain
3. Preserve interfaces so a later fine-tuned BERT-Tiny model can drop in without changing the entry flow

The key requirement for the MVP is interface shape and benchmarkability, not full retraining in this pass.

## 8. MCP Bridge Design

The MCP layer in this MVP is structural and local-first.

### 8.1 Why Include It

- It aligns the codebase with the resume statement `LLM + MCP`
- It cleanly separates action generation from Blender execution
- It leaves a clear upgrade path to a more formal MCP service later

### 8.2 MVP Shape

- `blender_client.py`
  - exposes `call_tool(action_name, params)`
- `blender_server.py`
  - exposes tool handlers that map to the 5 supported actions
- `blender_bridge.py`
  - translates MCP-style tool calls to local Blender execution

The server does not need full remote transport in the first iteration. A local in-process or local command bridge is acceptable.

## 9. Blender Execution Strategy

### 9.1 Execution Mode

Use local Blender Python execution through a bridge that can run Blender in background mode.

Recommended approach:

- generate or pass a Python execution payload
- call Blender in background mode
- execute validated actions against `bpy`
- save outputs under a deterministic local directory such as `outputs/`

### 9.2 Expected Outputs

- generated render image path
- optional `.blend` save path
- execution status
- normalized error messages

### 9.3 Error Handling

Handle these errors explicitly:

- unknown action
- missing required params
- unsupported primitive or light type
- target object not found
- Blender command execution failure
- render output failure

Failures should return structured errors, not only logs.

## 10. Testing and Benchmark

The project should include a minimal automated evaluation set.

### 10.1 Test Categories

- intent acceptance tests
  - valid Blender instructions are accepted
- rejection tests
  - unrelated requests are rejected
- parameter extraction tests
  - color, primitive, transform, and render parameters are normalized correctly
- action validation tests
  - malformed actions fail before execution
- execution tests
  - local Blender run creates expected output artifacts

### 10.2 Benchmark Dataset

Add a lightweight local benchmark file with:

- positive Blender commands
- negative non-Blender commands
- expected action labels
- expected key parameters

The benchmark script should print simple metrics such as:

- intent accuracy
- rejection accuracy
- parameter match rate
- execution pass rate

## 11. Review Strategy During Implementation

The user requested review after every step. Implementation should therefore follow this cadence:

1. write or modify one focused slice
2. run relevant local verification
3. review the result against the spec
4. only then proceed to the next slice

This is a process requirement for the project, not an optional preference.

## 12. Risks and Mitigations

### Risk: Existing code is tightly coupled to old domains

Mitigation:

- isolate Blender functionality in a new `blender_agent/` package
- keep existing shared interfaces only where they reduce effort

### Risk: Blender is unavailable locally

Mitigation:

- make the bridge detect Blender availability early
- keep execution errors explicit and testable

### Risk: Function-calling output is inconsistent

Mitigation:

- add a validator layer before execution
- constrain tool schema to only 5 actions

### Risk: Scope creep

Mitigation:

- cap the MVP to linear 1 to 3 action sequences
- avoid adding memory, scene planning, or advanced modeling features

## 13. Acceptance Criteria

This design is complete when the copied project can:

- run only from `/Users/hedyliang/Desktop/blender_agent`
- accept a natural-language Blender request
- reject obviously unrelated requests
- produce a structured action payload for the 5 supported actions
- execute at least the basic action flow locally through Blender Python
- return structured execution results including file paths or error messages
- run a small automated benchmark/test suite

## 14. Implementation Direction

Recommended implementation order:

1. establish Blender-specific models, validators, and MCP bridge interfaces
2. swap or isolate the action schema to the 5 Blender tools
3. route entry requests into Blender intent/reject and parsing flow
4. implement Blender background execution helpers
5. add tests and benchmark dataset

This order minimizes wasted work and makes each review checkpoint concrete.
