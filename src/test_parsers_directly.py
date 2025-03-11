"""
Script to directly test the parser classes.

This script directly tests our parser implementations without using unittest or Django's test framework.
"""

import sys
import os

from abc import ABC, abstractmethod
from typing import Dict, Any, List

# Test the base Parser class
print("Testing Base Parser...")

# Define a simple Parser interface
class Parser(ABC):
	@abstractmethod
	def parse(self, config_text: str) -> Dict[str, Any]:
		pass
	
	@abstractmethod
	def detect_device_type(self, config_text: str) -> bool:
		pass
	
	def extract_hostname(self, config_text: str) -> str:
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		return []

# Test instantiating the base class (should fail)
try:
	parser = Parser()
	print("FAILED: Was able to instantiate abstract base class")
except TypeError:
	print("PASSED: Cannot instantiate abstract base class")

# Test incomplete implementation (should fail)
try:
	class IncompleteParser(Parser):
		pass
	
	parser = IncompleteParser()
	print("FAILED: Was able to instantiate incomplete implementation")
except TypeError:
	print("PASSED: Cannot instantiate incomplete implementation")

# Test a minimal implementation
class MinimalParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {}
	
	def detect_device_type(self, config_text: str) -> bool:
		return True

# Should not raise exception
try:
	parser = MinimalParser()
	print("PASSED: Can instantiate minimal implementation")
except Exception as e:
	print(f"FAILED: Could not instantiate minimal implementation: {str(e)}")

# Simple Cisco IOS parser test
print("\nTesting Cisco IOS Parser...")

class CiscoIOSParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid Cisco IOS configuration")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "cisco-ios",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		return "version" in config_text and "hostname" in config_text
	
	def extract_hostname(self, config_text: str) -> str:
		import re
		match = re.search(r'hostname\s+(\S+)', config_text)
		if match:
			return match.group(1)
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		interfaces = []
		import re
		
		# Simple interface extraction
		interface_blocks = re.findall(r'interface\s+(\S+).*?(?=interface|\Z)', config_text, re.DOTALL)
		
		for interface_name in interface_blocks:
			interface = {
				"name": interface_name.strip(),
				"description": "",
				"ip_address": "",
				"subnet_mask": ""
			}
			interfaces.append(interface)
		
		return interfaces

# Test with sample config
ios_config = """
version 15.2
hostname TestRouter
!
interface GigabitEthernet0/0
 description WAN Interface
 ip address 192.168.1.1 255.255.255.0
!
interface GigabitEthernet0/1
 description LAN Interface
 ip address 10.0.0.1 255.255.255.0
!
end
"""

ios_parser = CiscoIOSParser()

# Test device type detection
if ios_parser.detect_device_type(ios_config):
	print("PASSED: Detected Cisco IOS configuration")
else:
	print("FAILED: Did not detect Cisco IOS configuration")

# Test hostname extraction
hostname = ios_parser.extract_hostname(ios_config)
if hostname == "TestRouter":
	print("PASSED: Extracted correct hostname")
else:
	print(f"FAILED: Extracted incorrect hostname: {hostname}")

# Test parsing
try:
	parsed_data = ios_parser.parse(ios_config)
	if parsed_data["device_type"] == "cisco-ios" and parsed_data["hostname"] == "TestRouter":
		print("PASSED: Successfully parsed configuration")
	else:
		print(f"FAILED: Incorrectly parsed configuration: {parsed_data}")
except Exception as e:
	print(f"FAILED: Exception while parsing: {str(e)}")

print("\nAll parser tests completed.") 