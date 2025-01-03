#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os.path

from src.utils import knowledge_base_path, circuit_types


def load_knowledge_base():
    knowledge_base = []

    for cno, circuit_type in enumerate(circuit_types):
        circuit_type_file_prefix = circuit_type.replace(" ", "_")

        # Read description
        with open(
            os.path.join(
                knowledge_base_path,
                f"{circuit_type_file_prefix}_description_symbol.temp",
            )
        ) as f:
            is_in_performance_metrics = False
            performance_metrics = ""
            for line in f:
                if line.strip().lower().startswith("4. performance"):
                    is_in_performance_metrics = True
                    continue
                if is_in_performance_metrics:
                    performance_metrics += line

        # Read netlist
        with open(
            os.path.join(
                knowledge_base_path,
                f"{circuit_type_file_prefix}_netlist_symbol.temp",
            )
        ) as f:
            netlist = f.read().replace("insert value of ", "")

        # Summarize the data into knowledge base
        knowledge_base.append(
            {
                "circuit_type": circuit_type,
                "performance": performance_metrics,
                "netlist": netlist,
            }
        )

    print(knowledge_base)
    return knowledge_base
