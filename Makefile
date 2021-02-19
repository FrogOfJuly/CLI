.PHONY: test mypy flake8 pylint run clean help

help:
	echo "make help\n make_run \n make run_flake8 \n make run_pylint \n make run_mypy make clean"

run:
	pip3 install -r requirements.txt
	python3 CLI/cli.py
test:
	pip3 install pytest
	cd tests
	pytest
	cd ..
run_flake8:
	pip3 install flake8
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
	flake8 . --count --exit-zero --max-complexity=10 --max-line-length=127 --statistics
run_pylint:
	pip3 install pylint
	PYLINT_THRESHOLD=9.0
	find CLI -type f -iname "*.py" ! -iname "__init__.py" | xargs -r pylint --disable=C0111 | tee pylint.txt || true
	score=$(sed -n 's/^Your code has been rated at \([-0-9.]*\)\/.*/\1/p' pylint.txt)
run_mypy:
	pip3 install mypy
	find CLI -type f -iname "*.py" ! -iname "__init__.py" | xargs -r mypy --pretty
clean:
	rm -r ./.mypy_cache
	rm -r ./tests/.pytest_cache