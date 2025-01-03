#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from zhipuai import ZhipuAI
from langchain_experimental.utilities import PythonREPL

from src.utils import (
    push_message,
    get_response,
    cleanup_code,
    cutoff_frequency_prompt,
)


def solve_cutoff(
    question: str,
    circuit_type: int,
    ai_client: ZhipuAI,
    knowledge_base: dict,
    messages: list,
):
    messages = push_message(
        cutoff_frequency_prompt.format(
            knowledge_base[circuit_type]["performance"]
        ),
        messages,
    )
    answer, messages = get_response(ai_client, messages)

    params = json.loads(cleanup_code(answer))
    # circuit_params = {}
    # cutoff_freqs = {}
    # for key in params.keys():
    #     if key in ["R", "L", "C"]:
    #         circuit_params[key] = params[key]
    #     else:
    #         cutoff_freqs[key] = params[key]

    repl = PythonREPL()
    output_dict = {}
    repl.run("from math import *")
    # for rlc in circuit_params:
    #     # val = PythonREPL.sanitize_input(circuit_params[rlc])
    #     val = float(circuit_params[rlc])
    #     freq = repl.run(f"{rlc} = {val}")
    # for cutoff in cutoff_freqs:
    #     # expr = PythonREPL.sanitize_input(cutoff_freqs[cutoff])
    #     expr = cutoff_freqs[cutoff]
    #     freq = repl.run(f"print({expr})")
    #     output_dict[cutoff] = freq
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
