"""
Base parser module defining the abstract Parser interface.

All device-specific parsers must implement this interface.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List


class Parser(ABC):
	"""
	Abstract base class for all device configuration parsers.
	
	All device-specific parsers must inherit from this class and implement
	the required methods.
	"""
	
	@abstractmethod
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""
		Parse the device configuration text into a structured format.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			Dict[str, Any]: A dictionary containing the parsed configuration data.
			The structure will include sections for hostname, interfaces, routes,
			VLANs, etc., depending on what's available in the configuration.
			
		Raises:
			ValueError: If the configuration cannot be parsed or is invalid.
		"""
		pass
	
	@abstractmethod
	def detect_device_type(self, config_text: str) -> bool:
		"""
		Determine if this parser can handle the given configuration text.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			bool: True if this parser can handle the configuration, False otherwise.
		"""
		pass
	
	def extract_hostname(self, config_text: str) -> str:
		"""
		Extract the hostname from the configuration.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			str: The extracted hostname, or an empty string if not found.
		"""
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""
		Extract interface information from the configuration.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			List[Dict[str, Any]]: A list of dictionaries, each representing
			an interface with its properties.
		"""
		return []
	
	def extract_acls(self, config_text: str) -> List[Dict[str, Any]]:
		"""
		Extract Access Control List (ACL) information from the configuration.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			List[Dict[str, Any]]: A list of dictionaries, each representing
			an ACL with its rules.
		"""
		return []
	
	def extract_vrfs(self, config_text: str) -> List[Dict[str, Any]]:
		"""
		Extract Virtual Routing and Forwarding (VRF) information from the configuration.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			List[Dict[str, Any]]: A list of dictionaries, each representing
			a VRF with its properties.
		"""
		return []
	
	def extract_routing(self, config_text: str) -> Dict[str, Any]:
		"""
		Extract routing information from the configuration.
		
		Args:
			config_text (str): The raw device configuration text.
			
		Returns:
			Dict[str, Any]: A dictionary containing routing information,
			including routing protocols, static routes, etc.
		"""
		return {} 