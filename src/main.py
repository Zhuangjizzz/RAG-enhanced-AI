#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from zhipuai import ZhipuAI

import sys
from src.solve import solve
from src.knowledge_base import load_knowledge_base
from src.utils import load_questions, output_path



def main():
    # 1. Initialization
    ai_client = ZhipuAI(
        # timeout=60,
        api_key="8449210524e61f79c004e9e8ea793c83.XS9kf5xyoUOOWEpQ",
    )

    # 2. Load the knowledge base
    knowledge_base = load_knowledge_base()

    # 3. Load the questions
    questions = load_questions()

    # 4. Process the questions
    for qno, question in enumerate(questions, start=1):
        # print(qno, question)
        print("******************************************************")
        print(f"QUESTION {qno}: {question}")
        print("******************************************************\n")
        output = solve(question, ai_client, knowledge_base)
        print(f"OUTPUT: {output}\n")
        with open(os.path.join(output_path, f"{qno}"), "w") as f:
            f.write(output)


if __name__ == "__main__":
    main()
