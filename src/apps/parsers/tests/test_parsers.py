"""
Tests for the parsers module.

This module contains unit tests for the parsers package, including:
- Base Parser interface
- Individual parser implementations
- Parser factory
"""

import unittest
from unittest.mock import patch, MagicMock, mock_open
from io import StringIO

from apps.parsers.parsers.base import Parser
from apps.parsers.parsers.cisco import CiscoIOSParser, CiscoASAParser, CiscoNexusParser
from apps.parsers.parsers.fortinet import FortiGateParser, FortiSwitchParser
from apps.parsers.parsers.juniper import JuniperJunOSParser
from apps.parsers.parsers.factory import ParserFactory
from apps.parsers.models import DeviceFile


class TestBaseParser(unittest.TestCase):
	"""Tests for the base Parser abstract class."""
	
	def test_base_parser_cannot_be_instantiated(self):
		"""Test that the base Parser class cannot be instantiated directly."""
		with self.assertRaises(TypeError):
			Parser()
	
	def test_base_parser_abstract_methods(self):
		"""Test that subclasses must implement abstract methods."""
		class IncompleteParser(Parser):
			pass
		
		with self.assertRaises(TypeError):
			IncompleteParser()
	
	def test_minimum_viable_parser(self):
		"""Test that a minimal implementation of Parser can be instantiated."""
		class MinimalParser(Parser):
			def parse(self, config_text):
				return {}
			
			def detect_device_type(self, config_text):
				return True
		
		# Should not raise exception
		parser = MinimalParser()
		self.assertIsInstance(parser, Parser)


class TestCiscoIOSParser(unittest.TestCase):
	"""Tests for the CiscoIOSParser implementation."""
	
	def setUp(self):
		"""Set up the test case."""
		self.parser = CiscoIOSParser()
		self.ios_config = """
		! Last configuration change at 14:03:55 UTC Mon Mar 16 2023
		version 15.2
		service timestamps debug datetime msec
		service timestamps log datetime msec
		no service password-encryption
		hostname ROUTER1
		!
		boot-start-marker
		boot-end-marker
		!
		enable secret 5 $1$XXXX$YYYYZZZZAAAA
		!
		no aaa new-model
		!
		interface GigabitEthernet0/0
		 description WAN Interface
		 ip address 192.168.1.1 255.255.255.0
		 duplex auto
		 speed auto
		!
		interface GigabitEthernet0/1
		 description LAN Interface
		 ip address 10.0.0.1 255.255.255.0
		 duplex auto
		 speed auto
		!
		ip classless
		ip route 0.0.0.0 0.0.0.0 192.168.1.254
		!
		access-list 100 permit ip any any
		access-list 101 deny ip host 192.168.1.100 any
		!
		line con 0
		line aux 0
		line vty 0 4
		 password cisco
		 login
		!
		end
		"""
	
	def test_detect_device_type(self):
		"""Test that the parser correctly identifies Cisco IOS configurations."""
		self.assertTrue(self.parser.detect_device_type(self.ios_config))
		
		non_ios_config = "set system host-name Firewall"
		self.assertFalse(self.parser.detect_device_type(non_ios_config))
	
	def test_extract_hostname(self):
		"""Test that the parser correctly extracts the hostname."""
		hostname = self.parser.extract_hostname(self.ios_config)
		self.assertEqual(hostname, "ROUTER1")
	
	def test_extract_interfaces(self):
		"""Test that the parser correctly extracts interfaces."""
		interfaces = self.parser.extract_interfaces(self.ios_config)
		self.assertEqual(len(interfaces), 2)
		
		# Check first interface
		self.assertEqual(interfaces[0]["name"], "GigabitEthernet0/0")
		self.assertEqual(interfaces[0]["description"], "WAN Interface")
		self.assertEqual(interfaces[0]["ip_address"], "192.168.1.1")
		self.assertEqual(interfaces[0]["subnet_mask"], "255.255.255.0")
		
		# Check second interface
		self.assertEqual(interfaces[1]["name"], "GigabitEthernet0/1")
		self.assertEqual(interfaces[1]["description"], "LAN Interface")
		self.assertEqual(interfaces[1]["ip_address"], "10.0.0.1")
		self.assertEqual(interfaces[1]["subnet_mask"], "255.255.255.0")
	
	def test_extract_acls(self):
		"""Test that the parser correctly extracts ACLs."""
		acls = self.parser.extract_acls(self.ios_config)
		self.assertEqual(len(acls), 2)
		
		# Check ACLs
		self.assertEqual(acls[0]["number"], "100")
		self.assertEqual(acls[0]["entries"][0]["action"], "permit")
		
		self.assertEqual(acls[1]["number"], "101")
		self.assertEqual(acls[1]["entries"][0]["action"], "deny")
	
	def test_parse(self):
		"""Test the complete parsing process."""
		parsed_data = self.parser.parse(self.ios_config)
		
		self.assertEqual(parsed_data["device_type"], "cisco-ios")
		self.assertEqual(parsed_data["hostname"], "ROUTER1")
		self.assertIn("interfaces", parsed_data)
		self.assertIn("acls", parsed_data)
		self.assertIn("routing", parsed_data)


class TestParserFactory(unittest.TestCase):
	"""Tests for the ParserFactory class."""
	
	def test_get_parser_for_cisco_ios(self):
		"""Test that the factory returns the correct parser for Cisco IOS."""
		config = "version 15.2\nhostname Router1\nip classless"
		parser = ParserFactory.get_parser(config)
		self.assertIsInstance(parser, CiscoIOSParser)
	
	def test_get_parser_for_cisco_asa(self):
		"""Test that the factory returns the correct parser for Cisco ASA."""
		config = "ASA Version 9.8\nhostname Firewall\naccess-list outside_access_in extended permit"
		parser = ParserFactory.get_parser(config)
		self.assertIsInstance(parser, CiscoASAParser)
	
	def test_get_parser_for_fortigate(self):
		"""Test that the factory returns the correct parser for FortiGate."""
		config = "config system global\nset hostname FGT01\nend\nconfig firewall policy"
		parser = ParserFactory.get_parser(config)
		self.assertIsInstance(parser, FortiGateParser)
	
	def test_get_parser_for_junos(self):
		"""Test that the factory returns the correct parser for JunOS."""
		config = "system {\n    host-name Router1;\n}\ninterfaces {\n    ge-0/0/0 {\n    }\n}"
		parser = ParserFactory.get_parser(config)
		self.assertIsInstance(parser, JuniperJunOSParser)
	
	def test_get_parser_for_unknown(self):
		"""Test that the factory returns None for unknown device types."""
		config = "This is not a valid network device configuration"
		parser = ParserFactory.get_parser(config)
		self.assertIsNone(parser)
	
	def test_get_parser_for_device_type(self):
		"""Test getting a parser by device type slug."""
		parser = ParserFactory.get_parser_for_device_type("cisco-ios")
		self.assertIsInstance(parser, CiscoIOSParser)
		
		parser = ParserFactory.get_parser_for_device_type("cisco-asa")
		self.assertIsInstance(parser, CiscoASAParser)
		
		parser = ParserFactory.get_parser_for_device_type("fortigate")
		self.assertIsInstance(parser, FortiGateParser)
		
		parser = ParserFactory.get_parser_for_device_type("juniper-junos")
		self.assertIsInstance(parser, JuniperJunOSParser)
		
		parser = ParserFactory.get_parser_for_device_type("unknown")
		self.assertIsNone(parser)


class TestDeviceFileParseMethod(unittest.TestCase):
	"""Tests for the DeviceFile.parse_file method."""
	
	def setUp(self):
		"""Set up the test case."""
		self.device_file = MagicMock(spec=DeviceFile)
		self.device_file.device_type = MagicMock()
		self.device_file.device_type.slug = "cisco-ios"
		self.device_file.device_type.name = "Cisco IOS"
		self.device_file.parsed = False
		self.device_file.parse_errors = ""
		
		self.config_text = """
		version 15.2
		hostname TestRouter
		interface GigabitEthernet0/0
		 ip address 192.168.1.1 255.255.255.0
		"""
		
		# Mock the file object
		file_mock = MagicMock()
		file_mock.seek.return_value = None
		file_mock.read.return_value = self.config_text.encode('utf-8')
		self.device_file.file = file_mock
	
	@patch('apps.parsers.parsers.cisco.CiscoIOSParser.parse')
	@patch('apps.parsers.parsers.factory.ParserFactory.get_parser_for_device_type')
	def test_parse_file_success(self, mock_get_parser, mock_parse):
		"""Test successful parsing of a device file."""
		# Mock the parser and parser factory
		mock_parser = MagicMock()
		mock_parser.parse.return_value = {"hostname": "TestRouter"}
		mock_get_parser.return_value = mock_parser
		
		# Call the method
		from apps.parsers.models import DeviceFile
		with patch.object(DeviceFile, 'save') as mock_save:
			result = DeviceFile.parse_file(self.device_file)
		
		# Verify the results
		self.assertTrue(result)
		self.assertTrue(self.device_file.parsed)
		self.assertEqual(self.device_file.parse_errors, "")
		mock_save.assert_called_once()
		mock_get_parser.assert_called_once_with("cisco-ios")
		self.device_file.file.seek.assert_called_once_with(0)
		mock_parser.parse.assert_called_once()
	
	@patch('apps.parsers.parsers.factory.ParserFactory.get_parser_for_device_type')
	def test_parse_file_no_parser(self, mock_get_parser):
		"""Test parsing when no parser is available."""
		# Mock the parser factory to return None
		mock_get_parser.return_value = None
		
		# Call the method
		from apps.parsers.models import DeviceFile
		with patch.object(DeviceFile, 'save') as mock_save:
			result = DeviceFile.parse_file(self.device_file)
		
		# Verify the results
		self.assertFalse(result)
		self.assertFalse(self.device_file.parsed)
		self.assertIn("No parser available", self.device_file.parse_errors)
		mock_save.assert_called_once()
	
	@patch('apps.parsers.parsers.factory.ParserFactory.get_parser_for_device_type')
	def test_parse_file_value_error(self, mock_get_parser):
		"""Test parsing when a ValueError occurs."""
		# Mock the parser to raise a ValueError
		mock_parser = MagicMock()
		mock_parser.parse.side_effect = ValueError("Invalid configuration")
		mock_get_parser.return_value = mock_parser
		
		# Call the method
		from apps.parsers.models import DeviceFile
		with patch.object(DeviceFile, 'save') as mock_save:
			result = DeviceFile.parse_file(self.device_file)
		
		# Verify the results
		self.assertFalse(result)
		self.assertFalse(self.device_file.parsed)
		self.assertIn("Parsing error", self.device_file.parse_errors)
		mock_save.assert_called_once()
	
	@patch('apps.parsers.parsers.factory.ParserFactory.get_parser_for_device_type')
	def test_parse_file_unexpected_error(self, mock_get_parser):
		"""Test parsing when an unexpected error occurs."""
		# Mock the parser to raise an exception
		mock_parser = MagicMock()
		mock_parser.parse.side_effect = Exception("Unexpected error")
		mock_get_parser.return_value = mock_parser
		
		# Call the method
		from apps.parsers.models import DeviceFile
		with patch.object(DeviceFile, 'save') as mock_save:
			result = DeviceFile.parse_file(self.device_file)
		
		# Verify the results
		self.assertFalse(result)
		self.assertFalse(self.device_file.parsed)
		self.assertIn("Unexpected error", self.device_file.parse_errors)
		mock_save.assert_called_once()


if __name__ == '__main__':
	unittest.main() 