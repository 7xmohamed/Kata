.PHONY: help test verify-docs verify-scripts

# Default target
.DEFAULT_GOAL := help

help:
	@echo "Usage: make [target]"
	@echo ""
	@echo "Targets:"
	@echo "  test              Run all tests and verifications"
	@echo "  verify-docs       Verify skills structure and metadata"
	@echo "  verify-scripts    Run smoke tests for python and shell scripts"

test: verify-docs verify-scripts

verify-docs:
	python3 scripts/verify-skills.py

verify-scripts:
	python3 scripts/run-smoke-tests.py

