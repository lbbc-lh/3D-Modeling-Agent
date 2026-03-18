# -*- coding: utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------


import json
import os
import copy
import traceback
import time
import requests
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from flask import Flask, jsonify, make_response
from flask_socketio import SocketIO, emit

import prompts
from blender_agent.executor import execute_actions
from blender_agent.models import build_execution_response
from blender_agent.planner import build_blender_actions, is_blender_request
from utils import logger
from utils.redis_tool import RedisClient
from client.arbitration import request_arbitration
from client.stream_chat import request_chat, process_chat
from client.reject import request_reject
from client.nlu import request_nlu
from client.rewrite import request_rewrite
from client.correlation import request_correlation
from utils.mq import RabbitMQProducer
from utils.observability import ensure_trace_id, log_event


socketio = SocketIO(cors_allowed_origins='*', async_mode='threading')
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
socketio.init_app(app)


TTL = 40
REDIS_KEY = "voice:last_service:{}"
redis_client = RedisClient() 
thread_pool = ThreadPoolExecutor(max_workers=10)
mq_producer = RabbitMQProducer()
SERVICE_NAME = os.getenv("SERVICE_NAME", "entry-service")


def publish_async_log(trace_id, sender_id, query, status, cost):
    payload = {
        "trace_id": trace_id,
        "sender_id": sender_id,
        "query": query,
        "status": status,
        "latency_ms": int(cost * 1000),
        "service": SERVICE_NAME,
    }
    mq_producer.publish(payload)


def handle_blender_request(query, trace_id):
    response = build_execution_response(
        query=query,
        trace_id=trace_id,
        intent="Blender建模",
        function="",
    )
    actions = build_blender_actions(query)
    response["actions"] = actions

    if not actions:
        response["intent"] = "拒识"
        response["function"] = "REJECT"
        response["execution"]["errors"] = ["no supported blender actions found"]
        return response

    execution = execute_actions(actions)
    response["function"] = actions[-1]["action"]
    response["execution"].update(execution)

    for result in execution.get("results", []):
        artifacts = result.get("artifacts", {})
        if "output_image" in artifacts and not response["execution"]["output_image"]:
            response["execution"]["output_image"] = artifacts["output_image"]
        if "scene_file" in artifacts and not response["execution"]["scene_file"]:
            response["execution"]["scene_file"] = artifacts["scene_file"]
    return response


@app.route("/health", methods=["GET"])
def check():
    response = make_response(
        jsonify(health="healthy"),
        200,
        {'content-type': 'application/json'}
    )
    return response


@socketio.on('connect')
def connected_msg():
    manager = socketio.server.manager
    connections_count = len(manager.rooms['/']) - 1
    logger.info(f'当前连接数: {connections_count}')
    logger.info('client connected.')


@socketio.on('disconnect')
def disconnect_msg():
    logger.info('client disconnected.')


def send_msg(nlu_result, func, frame, seq, cost, status):
    if func == "CHAT":
        intent = "闲聊百科" 
        intent_id = "439"
    else:
        intent = "拒识" 
        intent_id = "440"

    nlu_result["intent"] = intent
    nlu_result["intent_id"] = intent_id
    nlu_result["func"] = func
    nlu_result["frame"] = frame
    nlu_result["seq"] = seq
    nlu_result["cost"] = cost
    nlu_result["status"] = status

    emit(
        "request_nlu",
        json.dumps(nlu_result, ensure_ascii=False),
        broadcast=False
    )


def handle_chat(handler_bot, nlu_result, query, sender_id, begin):

    # 开始帧
    seq = 1
    nlu_result_begin = copy.deepcopy(nlu_result)
    send_msg(nlu_result_begin, "CHAT", "", seq, time.time() - begin, status=0)

    # 中间帧
    full_answer = ""
    for value in process_chat(handler_bot.result(), query, sender_id):
        nlu_result_chat = copy.deepcopy(nlu_result)
        send_msg(nlu_result_chat, "CHAT", value, seq, time.time() - begin, status=1)
        seq += 1
        full_answer += value
        logger.info(f"Chat Frame:{seq},content:{value}")

    # 结束帧
    if seq > 1:
        nlu_result_end = copy.deepcopy(nlu_result)
        send_msg(nlu_result_begin, "CHAT", "", seq, time.time() - begin, status=2)
        logger.info(f"Chat cost time: {time.time() - begin}")
        return True, full_answer
    else:
        logger.info(f"Chat cost time: {time.time() - begin}")
        return False, full_answer



@socketio.on('request_nlu')
def inference(req):
    begin = time.time()
    json_info = json.loads(req)
    query = json_info.get("query")
    enable_dm = json_info.get("enable_dm")
    sender_id = json_info.get("sender_id", "test")
    trace_id = ensure_trace_id(json_info.get("trace_id", "123"))

    nlu_template = {
        "query": query,
        "trace_id": trace_id,
        "intent": "",
        "intent_id": "",
        "function": "",
        "slots": {},
        "cost": time.time() - begin
    }
    try:
        ori_query = query
        logger.session.trace_id = trace_id
        logger.info("Request Params: {}".format(json_info))

        if is_blender_request(ori_query):
            blender_result = handle_blender_request(ori_query, trace_id)
            emit(
                "request_nlu",
                json.dumps(blender_result, ensure_ascii=False),
                broadcast=False
            )
            cost = time.time() - begin
            publish_async_log(trace_id, sender_id, ori_query, "ok", cost)
            log_event(
                SERVICE_NAME,
                trace_id,
                latency_ms=int(cost * 1000),
                status="ok",
                event="request_nlu",
                sender_id=sender_id,
            )
            return

        last_info = redis_client.get(REDIS_KEY.format(sender_id))
        last_domain, last_query, last_reject, last_answer = "", "", "", ""
        if last_info:
            last_domain, last_query, last_reject, last_answer = last_info.split("#")

        # Query改写
        query = request_rewrite(query, last_answer, sender_id)

        # 调用nlu语义
        handler_nlu = thread_pool.submit(request_nlu, query, trace_id, enable_dm)

        # 调用仲裁
        handler_arbitration = thread_pool.submit(request_arbitration, ori_query, sender_id)

        # 调拒识模型
        handler_reject = thread_pool.submit(request_reject, query, trace_id)

        # 调用相关性模型
        handler_correlation = thread_pool.submit(request_correlation, ori_query, sender_id)

        # 调用百科闲聊
        handler_bot = thread_pool.submit(request_chat, ori_query, sender_id)

        # 获取仲裁结果
        arbitration_result = handler_arbitration.result()

        logger.info(
            f"TraceID:{trace_id}, query:{query}, arbitration result: {arbitration_result}, cost time: {time.time() - begin}")

        # 开始仲裁
        if arbitration_result == "task":
            nlu_result = handler_nlu.result()
            # 技能
            if nlu_result.get("function", "") not in ["Unknown"]:
                redis_client.set(REDIS_KEY.format(sender_id), f"SKILL#{query}#1#", ex=TTL)
                emit(
                    "request_nlu",
                    json.dumps(
                        nlu_result,
                        ensure_ascii=False
                    ),
                    broadcast=False
                )
            else:
                send_msg(nlu_result, "REJECT", prompts.DEFAULT_NLG, 1, time.time() - begin, status=-1)
                logger.info(f"Query {query} has been rejected.")
        else:
            # 拒识
            reject_result = handler_reject.result()
            if reject_result == 0:
                correlation_result = handler_correlation.result()
                if correlation_result == "是":
                    reject_result = 1 
            if reject_result == 0:
                send_msg(nlu_template, "REJECT", "", 1, time.time() - begin, status=-1)
                logger.info(f"Query {query} has been rejected.")
            else:
                # 百科闲聊兜底
                is_hit_chat, full_answer = handle_chat(handler_bot, nlu_template, ori_query, sender_id, begin)
                if is_hit_chat:
                    redis_client.set(REDIS_KEY.format(sender_id), f"CHAT#{query}#{reject_result}#{full_answer}", ex=TTL)
        cost = time.time() - begin
        publish_async_log(trace_id, sender_id, query, "ok", cost)
        log_event(
            SERVICE_NAME,
            trace_id,
            latency_ms=int(cost * 1000),
            status="ok",
            event="request_nlu",
            sender_id=sender_id,
        )

    except Exception as e:
        logger.error(
            'TraceID:{}, Internal Server Error!'.format(trace_id))
        logger.error('{}'.format(e))
        traceback.print_exc()
        send_msg(nlu_template, "REJECT", "", 1, time.time() - begin, status=-1)
        cost = time.time() - begin
        publish_async_log(trace_id, sender_id, query, "error", cost)
        log_event(
            SERVICE_NAME,
            trace_id,
            latency_ms=int(cost * 1000),
            status="error",
            event="request_nlu",
            error=str(e),
        )

if __name__ == "__main__":
    socketio.run(
        app,
        allow_unsafe_werkzeug=True,
        host='0.0.0.0',
        port=os.getenv("FLASK_SERVER_PORT", 8080)
    )
