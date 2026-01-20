#!/bin/bash
source venv/bin/activate
flake8 app/
mypy app/ --ignore-missing-imports
pylint app/ || true  # Continue even if pylint fails
echo "Linting complete!"
