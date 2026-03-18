# -*- coding: utf-8 -*-

import json
import os
from datetime import datetime

import pika

from utils import logger
from utils.observability import log_event


SERVICE_NAME = os.getenv("SERVICE_NAME", "async-consumer")
RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "async_log_tasks")
ASYNC_LOG_FILE = os.getenv("ASYNC_LOG_FILE", "/app/log/async_tasks.log")


def persist_task(task: dict):
    os.makedirs(os.path.dirname(ASYNC_LOG_FILE), exist_ok=True)
    line = {
        "consume_time": datetime.utcnow().isoformat(),
        "task": task,
    }
    with open(ASYNC_LOG_FILE, "a", encoding="utf-8") as fp:
        fp.write(json.dumps(line, ensure_ascii=False) + "\n")


def consume():
    parameters = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(parameters)
    channel = connection.channel()
    channel.queue_declare(queue=RABBITMQ_QUEUE, durable=True)
    channel.basic_qos(prefetch_count=1)

    def callback(ch, method, properties, body):
        trace_id = "mq-consume"
        try:
            task = json.loads(body.decode("utf-8"))
            trace_id = str(task.get("trace_id", "mq-consume"))
            persist_task(task)
            log_event(
                SERVICE_NAME,
                trace_id,
                latency_ms=0,
                status="ok",
                event="consume_async_task",
            )
            ch.basic_ack(delivery_tag=method.delivery_tag)
        except Exception as exc:
            logger.error(f"consume task failed: {exc}")
            log_event(
                SERVICE_NAME,
                trace_id,
                latency_ms=0,
                status="error",
                event="consume_async_task",
                error=str(exc),
            )
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    channel.basic_consume(queue=RABBITMQ_QUEUE, on_message_callback=callback)
    logger.info(f"{SERVICE_NAME} waiting for queue={RABBITMQ_QUEUE}")
    channel.start_consuming()


if __name__ == "__main__":
    consume()
