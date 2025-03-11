"""
Script to test the DeviceFile parsing functionality using mocks.

This script simulates the DeviceFile.parse_file method to test how it interacts
with the parser factory and parser implementations without needing Django's ORM.
"""

import sys
import os
from typing import Dict, Any, Optional
from unittest.mock import MagicMock

# Mocked DeviceFile class
class DeviceFile:
	"""Mock of the DeviceFile model class."""
	
	def __init__(self, device_type_slug, file_content, parsed=False, parse_errors=""):
		self.device_type = MagicMock()
		self.device_type.slug = device_type_slug
		self.device_type.name = device_type_slug.replace('-', ' ').title()
		
		self.file = MagicMock()
		self.file.seek.return_value = None
		self.file.read.return_value = file_content.encode('utf-8')
		
		self.parsed = parsed
		self.parse_errors = parse_errors
	
	def save(self, update_fields=None):
		"""Mock save method."""
		print(f"DeviceFile saved with parsed={self.parsed}, errors='{self.parse_errors}'")
		return self
	
	def parse_file(self):
		"""
		Parse the configuration file and save results to the inventory.
		
		Returns:
			bool: True if parsing was successful, False otherwise.
		"""
		# Reset parsing status and errors
		self.parsed = False
		self.parse_errors = ""
		
		try:
			# Get appropriate parser using factory based on device type
			from mock_factory import ParserFactory
			
			parser = ParserFactory.get_parser_for_device_type(self.device_type.slug)
			if not parser:
				self.parse_errors = f"No parser available for device type: {self.device_type.name}"
				self.save(update_fields=['parsed', 'parse_errors'])
				return False
			
			# Read the configuration file
			self.file.seek(0)  # Ensure we're at the start of the file
			config_text = self.file.read().decode('utf-8', errors='replace')
			
			# Parse the configuration
			parsed_data = parser.parse(config_text)
			
			# In a real implementation, we would save the parsed data to the inventory
			print(f"Parsed data: {parsed_data}")
			
			# Update status
			self.parsed = True
			self.save(update_fields=['parsed', 'parse_errors'])
			return True
			
		except ValueError as e:
			# Handle parsing errors
			self.parse_errors = f"Parsing error: {str(e)}"
			self.save(update_fields=['parsed', 'parse_errors'])
			return False
		except Exception as e:
			# Handle unexpected errors
			self.parse_errors = f"Unexpected error: {str(e)}"
			self.save(update_fields=['parsed', 'parse_errors'])
			return False

# Create a mock parser factory module
with open('src/mock_factory.py', 'w') as f:
	f.write("""
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod

class Parser(ABC):
	@abstractmethod
	def parse(self, config_text: str) -> Dict[str, Any]:
		pass
	
	@abstractmethod
	def detect_device_type(self, config_text: str) -> bool:
		pass

class CiscoIOSParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		if "hostname" not in config_text:
			raise ValueError("Invalid Cisco IOS configuration: no hostname found")
		return {"device_type": "cisco-ios", "hostname": "TestRouter"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return True

class CiscoASAParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {"device_type": "cisco-asa", "hostname": "TestFirewall"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return True

class ParserFactory:
	@classmethod
	def get_parser_for_device_type(cls, device_type_slug: str) -> Optional[Parser]:
		parser_map = {
			'cisco-ios': CiscoIOSParser,
			'cisco-asa': CiscoASAParser,
		}
		
		parser_class = parser_map.get(device_type_slug.lower())
		if parser_class:
			return parser_class()
		
		return None
""")

print("Testing DeviceFile.parse_file...")

# Test successful parsing
device_file = DeviceFile("cisco-ios", """
hostname TestRouter
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
""")

print("\nTest 1: Successful parsing")
result = device_file.parse_file()
print(f"Result: {'Success' if result else 'Failure'}")
print(f"Parsed: {device_file.parsed}")
print(f"Parse errors: '{device_file.parse_errors}'")

# Test parsing error
device_file = DeviceFile("cisco-ios", """
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
""")

print("\nTest 2: Parsing error (missing hostname)")
result = device_file.parse_file()
print(f"Result: {'Success' if result else 'Failure'}")
print(f"Parsed: {device_file.parsed}")
print(f"Parse errors: '{device_file.parse_errors}'")

# Test no parser available
device_file = DeviceFile("unknown", """
hostname TestRouter
interface GigabitEthernet0/0
 ip address 192.168.1.1 255.255.255.0
""")

print("\nTest 3: No parser available")
result = device_file.parse_file()
print(f"Result: {'Success' if result else 'Failure'}")
print(f"Parsed: {device_file.parsed}")
print(f"Parse errors: '{device_file.parse_errors}'")

# Clean up mock file
os.remove('src/mock_factory.py')

print("\nAll DeviceFile parse tests completed.") 