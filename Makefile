lint:  # checks project for linting problems
	isort --diff --check .
	black --diff --check .
	flake8

lint-fix:  # fixes linting problems in project
	isort .
	black .
	flake8
