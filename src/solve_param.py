#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from zhipuai import ZhipuAI
from langchain_experimental.utilities import PythonREPL

from src.utils import (
    push_message,
    get_response,
    cleanup_code,
    circuit_param_calc_prompt,
)


def solve_param(
    question: str,
    circuit_type: int,
    ai_client: ZhipuAI,
    knowledge_base: dict,
    messages: list,
):
    messages = push_message(
        circuit_param_calc_prompt.format(
            knowledge_base[circuit_type]["performance"]
        ),
        messages,
    )
    answer, messages = get_response(ai_client, messages)

    params = json.loads(cleanup_code(answer))

    repl = PythonREPL()
    output_dict = {}
    repl.run("from math import *")
    for key in params["conditions"]:
        expr = params["conditions"][key]
        if isinstance(expr, str):
            expr = expr.replace("^", "**")
        repl.run(f"{key} = {expr}")
    for key in params["find"]:
        expr = params["find"][key]
        if isinstance(expr, str):
            expr = expr.replace("^", "**")
        ans = repl.run(f"print({expr})").strip()
        output_dict[key] = ans

    output = json.dumps(output_dict, indent=4)
    return output, messages
