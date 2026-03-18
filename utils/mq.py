# -*- coding: utf-8 -*-

import json
import os
from typing import Any, Dict

import pika

from utils import logger


RABBITMQ_URL = os.getenv("RABBITMQ_URL", "amqp://guest:guest@rabbitmq:5672/")
RABBITMQ_QUEUE = os.getenv("RABBITMQ_QUEUE", "async_log_tasks")


class RabbitMQProducer:
    def __init__(self, url: str = RABBITMQ_URL, queue_name: str = RABBITMQ_QUEUE):
        self.url = url
        self.queue_name = queue_name

    def publish(self, payload: Dict[str, Any]) -> bool:
        try:
            parameters = pika.URLParameters(self.url)
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            channel.queue_declare(queue=self.queue_name, durable=True)
            body = json.dumps(payload, ensure_ascii=False)
            channel.basic_publish(
                exchange="",
                routing_key=self.queue_name,
                body=body.encode("utf-8"),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            connection.close()
            return True
        except Exception as exc:
            logger.error(f"publish mq task failed: {exc}")
            return False
