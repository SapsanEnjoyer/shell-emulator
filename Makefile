PYTHON ?= python3

.PHONY: run test

run:
	./run.sh

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v
