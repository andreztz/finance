clean:
	@find ./ -name '*.pyc' -exec rm -f {} \;
	rm -rf .cache
	rm -rf build
	rm -rf dist 
	rm -rf *.egg-info
	rm -rf htmlcov
	rm -rf .tox/
	rm -rf docs/_build
	pip install -e '.[dev]' --upgrade --no-cache

install:
	pip install -e '.[dev]'

run:
	flask run

test:
	env FLASK_ENV=production pytest -v -s --cov=finance --pdb

cov-report:
	env FLASK_ENV=production pytest --cov=finance --cov-report=html -v -s
	python -m http.server --directory htmlcov 

check:
	check50 cs50/problems/2021/x/finance

check-local:
	check50 --local cs50/problems/2021/x/finance

