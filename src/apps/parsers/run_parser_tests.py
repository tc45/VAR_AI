"""
Script to run parser tests directly.

This script sets up the Django environment and runs the parser tests using unittest.
"""

import os
import sys
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'varai.settings')
django.setup()

# Now run the tests using unittest
import unittest
from apps.parsers.tests.test_parsers import TestBaseParser, TestCiscoIOSParser, TestParserFactory, TestDeviceFileParseMethod

if __name__ == '__main__':
	# Create a test suite with our test classes
	test_suite = unittest.TestSuite()
	test_suite.addTest(unittest.makeSuite(TestBaseParser))
	test_suite.addTest(unittest.makeSuite(TestCiscoIOSParser))
	test_suite.addTest(unittest.makeSuite(TestParserFactory))
	test_suite.addTest(unittest.makeSuite(TestDeviceFileParseMethod))
	
	# Run the test suite
	runner = unittest.TextTestRunner(verbosity=2)
	result = runner.run(test_suite)
	
	# Return non-zero exit code if tests failed
	sys.exit(not result.wasSuccessful()) 