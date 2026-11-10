# Komplette Pipeline:  make all      (LLM-Teil separat: make llm, braucht ANTHROPIC_API_KEY)
PY ?= python3

all: data baseline

setup:
	$(PY) -m pip install -r requirements.txt

data:
	bash scripts/fetch_data.sh
	$(PY) src/prepare_data.py

baseline:
	$(PY) src/train_baseline.py

llm:
	$(PY) src/llm_classify.py --n 200

.PHONY: all setup data baseline llm
