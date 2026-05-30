.PHONY: test verify-docs verify-scripts

test: verify-docs verify-scripts

verify-docs:
	python3 scripts/verify-skills.py

verify-scripts:
	python3 scripts/run-smoke-tests.py
