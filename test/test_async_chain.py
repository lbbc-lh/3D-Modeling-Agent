# -*- coding: utf-8 -*-

import json
import os
import tempfile
import unittest
from unittest.mock import MagicMock, patch

import async_consumer
from utils.mq import RabbitMQProducer


class AsyncChainTest(unittest.TestCase):
    def test_persist_task(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            target = os.path.join(tmpdir, "async_tasks.log")
            async_consumer.ASYNC_LOG_FILE = target
            task = {"trace_id": "t-1", "status": "ok"}
            async_consumer.persist_task(task)

            with open(target, "r", encoding="utf-8") as fp:
                line = fp.readline().strip()
                payload = json.loads(line)
                self.assertEqual(payload["task"]["trace_id"], "t-1")

    @patch("utils.mq.pika.BlockingConnection")
    def test_publish_success(self, mock_conn):
        connection = MagicMock()
        channel = MagicMock()
        connection.channel.return_value = channel
        mock_conn.return_value = connection

        producer = RabbitMQProducer("amqp://guest:guest@localhost:5672/", "q1")
        ok = producer.publish({"trace_id": "t-1"})

        self.assertTrue(ok)
        channel.queue_declare.assert_called_once_with(queue="q1", durable=True)
        channel.basic_publish.assert_called_once()


if __name__ == "__main__":
    unittest.main()
