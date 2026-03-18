# 测试报告（容器化改造）

## 1. 接口回归
- 覆盖接口：
  - `POST /intent-server/v1`
  - `POST /reject-server/v1`
  - `POST /chatnlu-server/v1`
  - `GET /health`（4个服务）
- 执行命令：
```bash
python -m unittest test/api_regression.py
```

## 2. 异步链路（RabbitMQ）
- 场景：入口服务发布“日志落盘任务”到 RabbitMQ，`async-consumer` 消费并写入 `log/async_tasks.log`
- 执行命令：
```bash
python -m unittest test/test_async_chain.py
python test/async_pipeline_test.py
```
- 判定标准：
  - 入队成功（producer 返回 True）
  - 消费成功（日志文件出现对应 `trace_id`）
  - 消费失败自动重试（`basic_nack(requeue=True)`）

## 3. 压测
- 脚本：
```bash
python test/load_test.py --url http://127.0.0.1:8080/health --total 500 --concurrency 50
```
- 记录项：
  - 成功率（success_rate）
  - p95 延迟（p95_ms）
  - 错误类型（网络超时/5xx）

## 4. 本地执行结果（示例模板）
- 执行时间：`2026-03-03`
- 运行环境：`docker compose 容器网络内执行`
- 接口回归：`4/4 通过`
- 异步链路单测：`2/2 通过`
- 压测命令：
```bash
python /app/test/load_test.py --url http://entry-service:8080/health --total 500 --concurrency 50
```
- 压测结果：
  - 成功率：`100% (500/500)`
  - 平均延迟：`18.95 ms`
  - p95：`38.72 ms`
  - 主要错误类型：`无`
