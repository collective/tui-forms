### Defensive settings for make:
#     https://tech.davis-hansson.com/p/make/
SHELL:=bash
.ONESHELL:
.SHELLFLAGS:=-xeu -o pipefail -O inherit_errexit -c
.SILENT:
.DELETE_ON_ERROR:
MAKEFLAGS+=--warn-undefined-variables
MAKEFLAGS+=--no-builtin-rules

# We like colors
# From: https://coderwall.com/p/izxssa/colored-makefile-for-golang-projects
RED=`tput setaf 1`
GREEN=`tput setaf 2`
RESET=`tput sgr0`
YELLOW=`tput setaf 3`

# Python checks
UV?=uv

# installed?
ifeq (, $(shell which $(UV) ))
  $(error "UV=$(UV) not found in $(PATH)")
endif

ROOT_FOLDER=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
GIT_FOLDER=$(ROOT_FOLDER)/.git
VENV_FOLDER=$(ROOT_FOLDER)/.venv

# Environment variables to be exported
export PYTHONWARNINGS := ignore

all: build

# Add the following 'help' target to your Makefile
# And add help text after each target name starting with '\#\#'
.PHONY: help
help: ## This help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

$(VENV_FOLDER): ## Install dependencies
	@echo "$(GREEN)==> Install environment$(RESET)"
	@uv sync --all-extras

.PHONY: sync
sync: $(VENV_FOLDER) ## Sync project dependencies
	@echo "$(GREEN)==> Sync project dependencies$(RESET)"
	@uv sync --all-extras

.PHONY: install
install: $(VENV_FOLDER) ## Install environment


.PHONY: clean
clean: ## Clean installation
	@echo "$(RED)==> Cleaning environment and build$(RESET)"
	@rm -rf $(VENV_FOLDER) .*_cache .coverage

############################################
# QA
############################################
.PHONY: lint
lint: ## Check and fix code base
	@echo "$(GREEN)==> Lint codebase$(RESET)"
	@uvx ruff@latest check --fix --config pyproject.toml

.PHONY: lint-mypy
lint-mypy: ## Check type hints
	@echo "$(GREEN)==> Check type hints$(RESET)"
	@uvx mypy src

.PHONY: lint-pyroma
lint-pyroma: ## Check package health
	@echo "$(GREEN)==> Check package health$(RESET)"
	@uvx pyroma .

.PHONY: lint-python-versions
lint-python-versions: ## Check python versions
	@echo "$(GREEN)==> Check package health$(RESET)"
	@uvx check-python-versions .

.PHONY: format
format: ## Check and fix code base formatting
	@echo "$(GREEN)==> Format codebase$(RESET)"
	@uvx ruff@latest check --select I --fix --config pyproject.toml
	@uvx ruff@latest format --config pyproject.toml

.PHONY: check
check: format lint lint-mypy  ## Check and fix code base

.PHONY: check-package
check-package: lint-pyroma lint-python-versions  ## Check package information and metadata


############################################
# Tests
############################################
.PHONY: test
test: $(VENV_FOLDER) ## run tests
	@uv run pytest

.PHONY: test-coverage
test-coverage: $(VENV_FOLDER) ## run tests with coverage
	@uv run pytest --cov=tui_forms --cov-report term-missing


############################################
# Documentation
############################################
.PHONY: docs-html
docs-html: $(VENV_FOLDER) ## Build HTML documentation
	@make -C ./docs html

.PHONY: docs-livehtml
docs-livehtml: $(VENV_FOLDER) ## Build documentation and serve it
	@make -C ./docs livehtml

.PHONY: docs-vale
docs-vale: $(VENV_FOLDER) ## Run vale on the documentation
	@make -C ./docs vale

.PHONY: docs-linkcheckbroken
docs-linkcheckbroken: $(VENV_FOLDER) ## Run checks for broken links
	@make -C ./docs linkcheckbroken

.PHONY: docs-test
docs-test: $(VENV_FOLDER) ## Run tests on the documentation
	@make -C ./docs test

############################################
# Release
############################################
.PHONY: changelog
changelog: ## Display the draft of the changelog
	@echo "🚀 Display the draft for the changelog"
	@uv run towncrier --draft

.PHONY: release
release: ## Release the package to pypi.org
	@echo "🚀 Release package"
	@uv run prerelease
	@uv run release
	@rm -Rf dist
	@uv build
	@uv publish
	@uv run postrelease
