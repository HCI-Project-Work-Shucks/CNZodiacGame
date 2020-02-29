.PHONY: all lint run

lint:
	pylint -E *.py && pyflakes *.py

run: lint
	python3 server.py
