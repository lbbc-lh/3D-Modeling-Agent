# 3D Modeling Agent

一个面向 Blender 的本地建模助手 Demo。  
它把自然语言请求转换为结构化建模动作，并通过 MCP 风格工具桥接调用 Blender Python，完成基础建模、材质设置、灯光相机配置和渲染输出。

## 功能

当前版本支持 5 个基础动作：

- `create_primitive`
- `transform_object`
- `apply_material`
- `setup_camera_light`
- `render_scene`

当前链路：

`自然语言 -> 动作规划 -> 参数校验 -> MCP 桥接 -> Blender 执行 -> 渲染输出`

## 项目结构

- [start.py](./start.py)：入口与请求路由
- [blender_agent](./blender_agent)：动作规划、校验与执行
- [mcp_core](./mcp_core)：MCP 风格工具桥接
- [function_call](./function_call)：Tool schema 与参数归一化
- [scripts/demo_blender_agent.py](./scripts/demo_blender_agent.py)：最小演示脚本
- [test](./test)：测试与 benchmark

## 快速开始

### 1. 配置 Blender 路径

```bash
export BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender"
```

### 2. 运行 Demo

```bash
BLENDER_BIN="/Applications/Blender.app/Contents/MacOS/Blender" \
PYTHONPATH=. \
python scripts/demo_blender_agent.py "创建一个红色立方体，添加相机和灯光，并渲染"
```

脚本会输出：

- 原始 query
- 动作序列
- 执行结果
- 渲染图片路径
- `.blend` 文件路径

## 测试

运行 Blender 相关测试：

```bash
PYTHONPATH=. python -m unittest discover -s test -p 'test_blender*.py'
```

## Benchmark

Benchmark 数据文件：

- [test/data/blender_benchmark.json](./test/data/blender_benchmark.json)

当前覆盖：

- Blender 请求识别
- 非 Blender 请求拒识
- 动作序列匹配
- 基础参数归一化

## 说明

- 当前版本更适合作为本地 Demo 和项目展示
- `planner` 还是最小实现，后续可升级为真实 LLM function calling
- Blender 意图识别和拒识模型还可以继续做领域化训练
