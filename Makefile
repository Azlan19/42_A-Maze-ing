install: # Install project dependencies
	pip install -r requirements.txt

run: # Execute the main script of your project
	python3 a_maze_ing.py config.txt

debug: # Run the main script in debug mode using Python’s built-in debugger
	python3 -m pdb a_maze_ing.py config.txt

clean: # Remove temporary files or caches
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true

lint: # Intrusted to add these in the subject
	flake8 .
	mypy . --warn-return-any --warn-unused-ignores --ignore-missing-imports \
		   --disallow-untyped-defs --check-untyped-defs

lint-strict: # Intrusted to add these in the subject
	flake8 .
	mypy . --strict