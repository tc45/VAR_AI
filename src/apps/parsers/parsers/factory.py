"""
Parser factory module.

This module provides a factory class that can automatically select the appropriate
parser based on the content of the configuration file.
"""

from typing import Optional, List, Type
from .base import Parser
from .cisco import CiscoIOSParser, CiscoASAParser, CiscoNexusParser
from .fortinet import FortiGateParser, FortiSwitchParser
from .juniper import JuniperJunOSParser


class ParserFactory:
	"""
	Factory class for creating device configuration parsers.
	
	This factory determines the appropriate parser to use based on the content
	of a configuration file.
	"""
	
	@classmethod
	def get_parser(cls, config_text: str) -> Optional[Parser]:
		"""
		Get the appropriate parser for the given configuration text.
		
		Args:
			config_text (str): The device configuration text.
			
		Returns:
			Optional[Parser]: An instance of a Parser that can handle the configuration,
							  or None if no compatible parser was found.
		"""
		parsers = cls._get_parser_classes()
		
		for parser_class in parsers:
			parser = parser_class()
			if parser.detect_device_type(config_text):
				return parser
		
		return None
	
	@classmethod
	def get_parser_for_device_type(cls, device_type_slug: str) -> Optional[Parser]:
		"""
		Get a parser for a specific device type slug.
		
		Args:
			device_type_slug (str): The slug/name of the device type.
			
		Returns:
			Optional[Parser]: An instance of a Parser for the device type,
							  or None if no compatible parser was found.
		"""
		parser_map = {
			'cisco-ios': CiscoIOSParser,
			'cisco-asa': CiscoASAParser,
			'cisco-nexus': CiscoNexusParser,
			'fortigate': FortiGateParser,
			'fortiswitch': FortiSwitchParser,
			'juniper-junos': JuniperJunOSParser
		}
		
		parser_class = parser_map.get(device_type_slug.lower())
		if parser_class:
			return parser_class()
		
		return None
	
	@classmethod
	def _get_parser_classes(cls) -> List[Type[Parser]]:
		"""
		Get a list of all available parser classes.
		
		Returns:
			List[Type[Parser]]: All parser classes defined in the system.
		"""
		return [
			CiscoIOSParser,
			CiscoASAParser,
			CiscoNexusParser,
			FortiGateParser,
			FortiSwitchParser,
			JuniperJunOSParser
		] 