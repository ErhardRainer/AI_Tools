"""
Führt alle Provider-Tests aus.

Verwendung:
    python LLM_Client/unittest/run_all_tests.py
    python LLM_Client/unittest/run_all_tests.py -v      # ausführlich
"""

import sys
import unittest
from pathlib import Path

# Sicherstellen, dass das unittest-Verzeichnis im Suchpfad ist
TEST_DIR = Path(__file__).parent
sys.path.insert(0, str(TEST_DIR))

loader = unittest.TestLoader()
suite = loader.discover(start_dir=str(TEST_DIR), pattern="test_*.py")

runner = unittest.TextTestRunner(verbosity=2 if "-v" in sys.argv else 1)
result = runner.run(suite)
sys.exit(0 if result.wasSuccessful() else 1)
