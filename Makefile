.PHONY: test install

install:
	python -m pip install -e .

test:
	python -m pytest -q
