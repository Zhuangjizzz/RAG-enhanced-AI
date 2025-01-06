# LLM4Analog
## Background
Contemporary mainstream large language models possess excellent analytical, explanatory, and logical reasoning abilities. However, when it comes to more complex tasks such as circuit netlist analysis and design, as well as deriving and calculating circuit-related formulas, current large language models may struggle to perform these tasks effectively.

An agent can enhance a model's ability in the field of circuit design without the need for extensive resource-consuming training. It can integrate a set of tools and libraries to create complex natural language processing workflows that can combine various data sources, tools, and external services. The integration of Retrieval-Augmented Generation (RAG) and computational tools can significantly improve the performance of large language models in the domain of circuit design simulation.
## Project Description
This design involves constructing an Agent framework to answer questions related to the design of passive filter circuits composed of resistors (R), inductors (L), and capacitors (C). For a specific type of filter, two files are provided to describe the circuit (including circuit structure, function, transfer function, and performance metrics) and the netlist, totaling 16 files. We utilize these knowledge bases to enhance the capabilities of the large model in order to answer three specific types of questions and return the output in the specified format.

### type1: netlist generation
input：str
```
[
“Give the netlist of parallel RLC bandpass filter with a R=1.5kOhms resistor and a L=7mH inductor and a C=5.2nF capacitor”
]
```
output：str netlist
```
Vin in 0 AC 1
R in out 1.5k
C out 0 5.2n
L out 0 7m
.END
```
### type2: cutoff frequency calculation
input：str
```
[
    “Given a R=1.5kOhms resistor, a L=7mH inductor and a C=5.2nF capacitor, calculate the cutoff frequency of parallel RLC bandpass filter”
]
```
output：dict
```
{
"omega_c1": "1.02e+05",
"omega_c2": "2.30e+05"
}
```
### type3: circuit parameter calculation
input：str
```
[
    “Design a parallel RLC bandpass filter with \\beta=129krad/s \\omega_0=166krad/s , currently I have a R=1.5kOhms resistor, a L=7mH inductor, tell me which capacitor value should I choose, the C is in nF units”
]
```
output：dict
```
{
"C": "5.184248180328889e-9"
}
```

This project uses the GLM-4-0520 model provided by Zhipu AI, with the model's API interface already included in the code. The question.json file contains the test questions, and the output files for each question are located in the output folder.
## Detailed Design and Functionality
### overall framework
![framework](img/framework.png)

### Agents Overflow
The input question is first classified into three agents through a classification agent: netlist generation, cutoff frequency calculation, and circuit parameter calculation. The corresponding agent will use lanchain's RAG tool, extracting the knowledge in the knowledge base then return to the prompt, thus enhancing the agent's ability to answer the question. The agent will also use the Python REPL tool to calculate the value of cutoff frequency and circuit parameters if necessary.

### RAG Usage

It uses a custom-made knowledge indexer for knowledge base searching!

For cutoff frequency and circuit parameter calculation, it uses RAG to help the prompt.

This RAG does not use semantic things such as TF-IDF, etc.
Instead, it just reads the circuit netlists and descriptions in a bare-metal way, and divide into
parts that are possibly useful for our tasks.

### Tool Usage

It uses Python REPL if the question requires calculation.

In our program, the LLM does not calculate values. Instead, its output information contains
expressions that are available for the program executing in the Python REPL.

The detailed code is in `src/solve_param.py`.The following is the code snippet.

```python
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
```

## Directory Structure
- `question.json` - the questions to be answered
- `output` - the directory to save output files
- `knowledge_base` - knowledge base for RAG-enhanced LLM
- `src` - programs

## Requirements
- run `conda create -n llm4analog python=3.10` to create a new environment
- run `conda activate llm4analog` to activate the environment
- run `pip install -r requirements.txt` to install the required packages

## How to Run?

```bash
export PYTHONPATH=.
conda activate llm4analog
python src/main.py
```
You can also see the dialogues on the screen.

## In/Output Example
### Input
```
[
"Give the netlist of RL low pass filter with a R=1.5kOhms resistor and a L=9.375mH inductance",
]
```
### Output
```
******************************************************
QUESTION 1: Give the netlist of RL low pass filter with a R=1.5kOhms resistor and a L=9.375mH inductance
******************************************************
// Classification agent

USER: Which type of question is the following question? Return only the answer's alphabetical index. The question type can only be one of the following.
A. Netlist generation
B. Cutoff frequency calculation
C. Component parameter calculation

Give the netlist of RL low pass filter with a R=1.5kOhms resistor and a L=9.375mH inductance

ASSISTANT: A

USER: Which type of circuit is discussed in the above question? Return only the answer's numerical index. The circuit type can only be one of the following.
0. RC lowpass
1. RC highpass
2. RL lowpass
3. RL highpass
4. series RLC bandpass
5. parallel RLC bandpass
6. series RLC bandreject
7. parallel RLC bandreject

ASSISTANT: 2

// Netlist generation agent

USER: What are the circuit parameters in the question? Return the answer in the JSON format. The circuit parameters can be two or three of "R", "L", and "C" depending on the circuit type. Do not return anything other than the JSON. The values must be in a string with SI unit prefixes if necessary. For example, an RC circuit with R=1.5kOhm and C=22.5uF should be represented as {"R": "1.5k", "C": "22.5u"}.

ASSISTANT: {"R": "1.5k", "L": "9.375m"}

// Netlist output

OUTPUT: Vin in 0 AC 1
L in out 9.375m
R out 0 1.5k
.END
```
And the final output will be saved in the `output` directory.