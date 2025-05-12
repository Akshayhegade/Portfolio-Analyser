#!/usr/bin/env python3
import unittest
import sys
import os

def run_tests(test_type=None):
    """
    Run the specified tests or all tests if no type is specified.
    
    Args:
        test_type (str, optional): Type of tests to run ('unit', 'integration', or None for all)
    
    Returns:
        bool: True if all tests pass, False otherwise
    """
    # Ensure we're in the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Discover and run tests
    if test_type == 'unit':
        test_suite = unittest.defaultTestLoader.discover('tests/unit', pattern='test_*.py')
        print("Running unit tests...")
    elif test_type == 'integration':
        test_suite = unittest.defaultTestLoader.discover('tests/integration', pattern='test_*.py')
        print("Running integration tests...")
    else:
        test_suite = unittest.defaultTestLoader.discover('tests', pattern='test_*.py')
        print("Running all tests...")
    
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    # Parse command line arguments
    test_type = None
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type not in ['unit', 'integration']:
            print(f"Invalid test type: {test_type}")
            print("Usage: python run_tests.py [unit|integration]")
            sys.exit(1)
    
    # Run tests and exit with appropriate status code
    success = run_tests(test_type)
    sys.exit(0 if success else 1)
