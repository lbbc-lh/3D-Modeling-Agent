# -*- coding:utf-8 -*-
# --------------------------------------------
# 项目名称: LLM任务型对话Agent
# 版权所有  ©2025丁师兄大模型
# 生成时间: 2025-05
# --------------------------------------------

import os
import re
import json
import random
import requests
import base64
import time
import torch
import uvicorn
import numpy as np
import torch.nn.functional as F
from importlib import import_module
from fastapi import FastAPI, Request
from utils import logger
from utils.observability import ensure_trace_id, log_event


## 创建FastAPI应用
app = FastAPI()
SERVICE_NAME = os.getenv("SERVICE_NAME", "intent-service")


dataset = "intent" # 数据
model_name = "bert"  # 模型
x = import_module('models.' + model_name)
config = x.Config(dataset)
model = x.Model(config).to(config.device)
state_dict = torch.load(config.save_path, map_location=config.device)
model.load_state_dict(state_dict)
model.eval()
PAD, CLS = '[PAD]', '[CLS]'
TOPK = 5


def predict(query):
    with torch.no_grad():
        token = config.tokenizer.tokenize(query)
        token = [CLS] + token
        seq_len = len(token)
        mask = []
        token_ids = config.tokenizer.convert_tokens_to_ids(token)
        if len(token) < config.pad_size:
            mask = [1] * len(token_ids) + [0] * (config.pad_size - len(token))
            token_ids += ([0] * (config.pad_size - len(token)))
        else:
            mask = [1] * config.pad_size
            token_ids = token_ids[:config.pad_size]
            seq_len = config.pad_size

        x = torch.LongTensor([token_ids]).to(config.device)
        seq_len = torch.LongTensor([seq_len]).to(config.device)
        mask = torch.LongTensor([mask]).to(config.device)
        texts = (x, seq_len, mask)
        output = model(texts)
        prob = F.softmax(output,dim=-1).cpu().numpy()[0]
        index = np.argsort(-prob)[:TOPK]

        return index, prob[index] 


@app.post("/intent-server/v1")
async def inference(request: Request):
    begin = time.time()
    json_info = await request.json()
    query = json_info.get("query")
    trace_id = ensure_trace_id(json_info.get("trace_id"))

    result = {}
    try:
        response, score = predict(query)
        status = "ok"
    except:
        response, score = [3] * TOPK, [1.0] * TOPK
        status = "error"

    result["data"] = ",".join([str(k) for k in response])
    result["score"] = ",".join([str(k) for k in score])
    logger.info("Trace ID: {}, Request: {}, response: {}, confidence: {}".format(
        trace_id, query, result["data"], result["score"]))
    log_event(
        SERVICE_NAME,
        trace_id,
        latency_ms=int((time.time() - begin) * 1000),
        status=status,
        event="intent_infer",
    )

    return result 


@app.get("/health")
async def health():
    return {"health": "healthy"}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8008, workers=1)  # 在指定端口和主机上启动应用
