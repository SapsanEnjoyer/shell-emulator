PYTHON ?= python3

.PHONY: run test vfs

run: vfs
	./run.sh

test:
	PYTHONPATH=src $(PYTHON) -m unittest discover -s tests -v

vfs:
	$(PYTHON) tools/make_vfs.py
