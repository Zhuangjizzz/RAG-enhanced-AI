#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

# %% General Constants
ai_model = "glm-4-0520"

question_file = "question.json"
output_path = "output"
knowledge_base_path = "knowledge_base"

circuit_types = [
    "RC lowpass",
    "RC highpass",
    "RL lowpass",
    "RL highpass",
    "series RLC bandpass",
    "parallel RLC bandpass",
    "series RLC bandreject",
    "parallel RLC bandreject",
]


# %% Functions
def load_questions():
    import json

    with open(question_file, "r") as f:
        questions = json.load(f)
    return questions


def push_message(message, messages: list):
    messages.append({"role": "user", "content": message})
    print(f"USER: {message}\n")
    return messages


def get_response(ai_client, messages: list):
    response = ai_client.chat.completions.create(
        model=ai_model, messages=messages, temperature=0.1
    )
    answer = response.choices[0].message.content
    messages.append({"role": "assistant", "content": answer})
    print(f"ASSISTANT: {answer}\n")
    return answer, messages


def cleanup_code(code: str):
    clean_code = ""
    for line in code.split("\n"):
        if not line.strip().startswith("```"):
            clean_code += line + "\n"
    return clean_code


def is_float(s):
    float_pattern = re.compile(r"^[-+]?[0-9]*\.?[0-9]+([eE][-+]?[0-9]+)?$")
    return bool(float_pattern.match(s))


# Example usage:
print(is_float("3.14"))  # True
print(is_float("314"))  # True, because it can be converted to a float
print(is_float("hello"))  # False


# %% Prompts

question_type_prompt = """
Which type of question is the following question? Return only the answer's \
alphabetical index. The question type can only be one of the following.
A. Netlist generation
B. Cutoff frequency calculation
C. Component parameter calculation

{0}
""".strip()

circuit_type_prompt = (
    """
Which type of circuit is discussed in the above question? Return only the \
answer's numerical index. The circuit type can only be one of the following.
"""
    + "\n".join(
        [f"{i}. {circuit}" for i, circuit in enumerate(circuit_types, start=0)]
    )
    + "\n"
).strip()

circuit_parameter_prompt = """
What are the circuit parameters in the question? Return the answer in the \
JSON format. The circuit parameters can be two or three of "R", "L", and "C" \
depending on the circuit type. Do not return anything other than the JSON. \
The values must be in a string with SI unit prefixes if necessary. \
For example, an RC circuit with R=1.5kOhm and C=22.5uF should be represented \
as {"R": "1.5k", "C": "22.5u"}.
""".strip()

cutoff_frequency_prompt = """
What are the circuit parameters and the expression(s) to calculate \
cutoff frequency(ies) in the question? \
Return the answer in the JSON format of "conditions" and "find" as in the
example. Use strict JSON and avoid comments. \
The circuit parameters can be two or \
three of "R", "L", and "C" depending on the circuit type. \
The cutoff frequency(ies) is in rad/s, and should have one or two \
depending on the circuit structure. \
The expression(s) for cutoff frequency(ies) can only use R, L, C, \
beta, and omega_0, as variables. \
The expression(s) for beta and omega_0 can only use R, L, and C as variables. \
The parameters beta and omega_0 does not exist in RL circuits or RC circuits. \
The order of return should be the order of solving. \
Do not return anything other than the JSON. \
The values must be either in a floating point number for RLC parameters, \
or a string containing the Python expression to calculate the cutoff \
frequency.
The Python expressions should be executable in the Python REPL. \
Example return: {{
    "conditions": {{"R": 1.5e3, "L": 75e-9, "C": 22.5e-6, \
"beta": "R/(2*L)", "omega_0": "1/sqrt(L*C)"}},
    "find": {{"omega_c1": "1/sqrt(L*C)", "omega_c2": "1/(R*C)"}}
}}

If this is an RLC circuit, you may have to think first how to calculate
beta and omega_0, and then use them to calculate the cutoff frequencies.

Here is some context showing how to find the cutoff frequency:
{0}
""".strip()

circuit_param_calc_prompt = """
What are the known parameters and the expression(s) to calculate the \
shown question? \
Return the answer in the JSON format of "conditions" and "find" as in the \
example. Use strict JSON and avoid comments. \
If necessary, you can list the intermediate results as expressions in the
"conditions" part. \
List the conditions as floating points as provided, or strings if they can
be calculated. \
In the "find" part, there should be only "R", "L", or "C" as keys, \
or a combination of them. \
Do not return anything other than the JSON. \
The expressions should be executable in the Python REPL. \
Be aware of unit conversion.

Example question: There is a R=220Ohms resistor, tell me which capacitor \
value should I choose, the C is in uF units. \
I want to design a low pass filter with \\omega_c=89Mrad/s.
Example return: {{
    "conditions": {{"omega_c": 89e6, "R": 220}},
    "find": {{"omega_c": "1/(R*omega_c)/1e-6"}}
}}

If this is an RLC circuit, you may consider design with the help of \
beta and omega_0, and then use them to calculate the results. \
If this is an RC or LC circuit, it should not have beta or omega_0.


Here is some context showing how to find the cutoff frequency:
{0}
""".strip()
