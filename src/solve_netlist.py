#!/usr/bin/env python
# -*- coding: utf-8 -*-

# from collections import defaultdict
import json
from zhipuai import ZhipuAI

from src.utils import (
    push_message,
    get_response,
    cleanup_code,
    circuit_parameter_prompt,
)


def solve_netlist(
    question: str,
    circuit_type: int,
    ai_client: ZhipuAI,
    knowledge_base: dict,
    messages: list,
):
    messages = push_message(circuit_parameter_prompt, messages)
    answer, messages = get_response(ai_client, messages)

    params = json.loads(cleanup_code(answer))

    output = knowledge_base[circuit_type]["netlist"].format(**params)
    return output, messages
