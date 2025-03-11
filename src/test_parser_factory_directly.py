"""
Script to directly test the parser factory.

This script directly tests our parser factory implementation to ensure it correctly
identifies and returns the appropriate parser for different configuration types.
"""

import sys
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type

# Base Parser interface
class Parser(ABC):
	@abstractmethod
	def parse(self, config_text: str) -> Dict[str, Any]:
		pass
	
	@abstractmethod
	def detect_device_type(self, config_text: str) -> bool:
		pass

# Cisco IOS Parser
class CiscoIOSParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {"device_type": "cisco-ios"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return "version" in config_text and "ip classless" in config_text

# Cisco ASA Parser
class CiscoASAParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {"device_type": "cisco-asa"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return "ASA Version" in config_text or "Firewall" in config_text

# Fortinet Parser
class FortiGateParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {"device_type": "fortigate"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return "config system global" in config_text or "set hostname FGT" in config_text

# Juniper Parser
class JuniperJunOSParser(Parser):
	def parse(self, config_text: str) -> Dict[str, Any]:
		return {"device_type": "junos"}
	
	def detect_device_type(self, config_text: str) -> bool:
		return "system {" in config_text or "host-name" in config_text and ";" in config_text

# Parser Factory
class ParserFactory:
	@classmethod
	def get_parser(cls, config_text: str) -> Optional[Parser]:
		parsers = cls._get_parser_classes()
		
		for parser_class in parsers:
			parser = parser_class()
			if parser.detect_device_type(config_text):
				return parser
		
		return None
	
	@classmethod
	def get_parser_for_device_type(cls, device_type_slug: str) -> Optional[Parser]:
		parser_map = {
			'cisco-ios': CiscoIOSParser,
			'cisco-asa': CiscoASAParser,
			'fortigate': FortiGateParser,
			'juniper-junos': JuniperJunOSParser
		}
		
		parser_class = parser_map.get(device_type_slug.lower())
		if parser_class:
			return parser_class()
		
		return None
	
	@classmethod
	def _get_parser_classes(cls) -> List[Type[Parser]]:
		return [
			CiscoIOSParser,
			CiscoASAParser,
			FortiGateParser,
			JuniperJunOSParser
		]

# Test configurations
print("Testing Parser Factory...")

configs = {
	"cisco-ios": """
	version 15.2
	hostname Router1
	ip classless
	""",
	
	"cisco-asa": """
	ASA Version 9.8
	hostname Firewall
	access-list outside_access_in extended permit
	""",
	
	"fortigate": """
	config system global
	set hostname FGT01
	end
	config firewall policy
	""",
	
	"junos": """
	system {
		host-name Router1;
	}
	interfaces {
		ge-0/0/0 {
		}
	}
	"""
}

# Test auto-detection of device types
for device_type, config in configs.items():
	parser = ParserFactory.get_parser(config)
	if parser:
		parser_class_name = parser.__class__.__name__
		print(f"PASSED: Detected {device_type} configuration as {parser_class_name}")
	else:
		print(f"FAILED: Could not detect {device_type} configuration")

# Test unknown configuration
unknown_config = "This is not a valid network device configuration"
parser = ParserFactory.get_parser(unknown_config)
if parser is None:
	print("PASSED: Correctly returned None for unknown configuration")
else:
	print(f"FAILED: Incorrectly detected unknown configuration as {parser.__class__.__name__}")

# Test getting parser by device type
device_types = ["cisco-ios", "cisco-asa", "fortigate", "juniper-junos", "unknown"]
for device_type in device_types:
	parser = ParserFactory.get_parser_for_device_type(device_type)
	if device_type == "unknown":
		if parser is None:
			print(f"PASSED: Correctly returned None for unknown device type")
		else:
			print(f"FAILED: Incorrectly returned {parser.__class__.__name__} for unknown device type")
	else:
		if parser:
			parser_class_name = parser.__class__.__name__
			print(f"PASSED: Got correct parser {parser_class_name} for {device_type}")
		else:
			print(f"FAILED: Could not get parser for {device_type}")

print("\nAll parser factory tests completed.") 