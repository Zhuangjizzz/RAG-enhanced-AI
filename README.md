# LLM4Analog
## Directory Structure
- `question.json` - the questions to be answered
- `output-example` - the example of output
- `output` - the directory to save output files
- `knowledge_base` - knowledge base for RAG-enhanced LLM
- `src` - programs

## Requirements
run `conda activate llm4analog` to activate application environment

## How to Run?

```bash
export PYTHONPATH=.
conda activate llm4analog
python src/main.py
```

You may see the dialogues on the screen.

## Does it use RAG?

Yes!

It uses a custom-made knowledge indexer for knowledge base searching!

For cutoff frequency and circuit parameter calculation, it uses RAG to help the prompt.

This RAG does not use semantic things such as TF-IDF, etc.
Instead, it just reads the circuit netlists and descriptions in a bare-metal way, and divide into
parts that are possibly useful for our tasks.

## Does it use tools?

Yes!

It uses Python REPL if the question requires calculation.

In our program, the LLM does not calculate values. Instead, its output information contains
expressions that are available for the program executing in the Python REPL.

