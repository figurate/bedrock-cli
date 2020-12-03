.PHONY: init test build deploy

init:
	pip install -r requirements.txt

test:
	py.test tests

build:
	python3 setup.py sdist bdist_wheel

deploy:
	twine upload dist/*