#!/usr/bin/env python
# -*- coding: utf-8 -*-

from zhipuai import ZhipuAI

from src.solve_netlist import solve_netlist
from src.solve_cutoff import solve_cutoff
from src.solve_param import solve_param
from src.utils import (
    push_message,
    get_response,
    question_type_prompt,
    circuit_type_prompt,
)


def solve(question: str, ai_client: ZhipuAI, knowledge_base: dict) -> str:
    messages = []

    try:

        # Get the question type
        messages = push_message(
            question_type_prompt.format(question), messages
        )
        answer, messages = get_response(ai_client, messages)
        question_type = answer[0].upper()

        # Get the circuit type
        messages = push_message(circuit_type_prompt, messages)
        answer, messages = get_response(ai_client, messages)
        circuit_type = int(answer[0])

        if question_type == "A":
            output, messages = solve_netlist(
                question, circuit_type, ai_client, knowledge_base, messages
            )
        elif question_type == "B":
            output, messages = solve_cutoff(
                question, circuit_type, ai_client, knowledge_base, messages
            )
        elif question_type == "C":
            output, messages = solve_param(
                question, circuit_type, ai_client, knowledge_base, messages
            )

    except Exception as e:
        print(f"Error: {e} in line {e.__traceback__.tb_lineno}")
        return ""

    return output
