CURRENT_PYTHON_VERSION := $(shell python --version 2>&1)
PROJECT_DIR=$(shell pwd)
REQUIRED_PYTHON_VERSION := 3.12

python-version:
	@echo "Checking python version..."
	@echo "Current python version: ${CURRENT_PYTHON_VERSION}"
	@echo "Required python version: ${REQUIRED_PYTHON_VERSION}"
	@python --version | grep -q "Python 3.12" && echo "Python 3.12 is installed. You deserve a cookie!" \
	|| (echo "Python 3.12 is NOT installed" && exit 1)

install: python-version
	@echo "Installing dependencies..."
	pip install -r requirements.txt
	@echo "Adding project directory to PYTHONPATH..."
	@export PYTHONPATH="${PROJECT_DIR}:${PYTHONPATH}"
	@echo "PYTHONPATH set to ${PROJECT_DIR}"
