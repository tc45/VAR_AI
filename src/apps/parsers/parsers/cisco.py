"""
Parsers for Cisco network devices.

This module contains parser implementations for various Cisco device types:
- Cisco IOS (Routers and Switches)
- Cisco ASA (Firewalls)
- Cisco Nexus (Data Center Switches)
"""

import re
from typing import Dict, Any, List
from .base import Parser


class CiscoIOSParser(Parser):
	"""Parser for Cisco IOS devices (routers and switches)."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""
		Parse Cisco IOS configuration.
		
		Args:
			config_text (str): The raw Cisco IOS configuration text.
			
		Returns:
			Dict[str, Any]: Structured configuration data.
			
		Raises:
			ValueError: If the configuration is not valid Cisco IOS.
		"""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid Cisco IOS configuration.")
		
		hostname = self.extract_hostname(config_text)
		interfaces = self.extract_interfaces(config_text)
		acls = self.extract_acls(config_text)
		vrfs = self.extract_vrfs(config_text)
		routing = self.extract_routing(config_text)
		
		return {
			"device_type": "cisco_ios",
			"hostname": hostname,
			"interfaces": interfaces,
			"acls": acls,
			"vrfs": vrfs,
			"routing": routing
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a Cisco IOS device."""
		# Look for typical Cisco IOS indicators
		ios_indicators = [
			r'version \d+\.\d+',
			r'boot system flash',
			r'service\s+',
			r'ip classless'
		]
		
		# Check if at least one indicator is present
		for indicator in ios_indicators:
			if re.search(indicator, config_text, re.IGNORECASE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from Cisco IOS configuration."""
		hostname_match = re.search(r'^hostname\s+(.+)$', config_text, re.MULTILINE)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interface configurations from Cisco IOS."""
		interfaces = []
		
		# Find all interface blocks
		interface_blocks = re.findall(
			r'^interface\s+(.+?)$\s+(.+?)(?=^!|^interface|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for interface_name, interface_config in interface_blocks:
			interface = {
				"name": interface_name.strip(),
				"description": "",
				"ip_address": "",
				"subnet_mask": "",
				"enabled": True,
				"vrf": "",
				"config": interface_config.strip()
			}
			
			# Extract description
			desc_match = re.search(r'description\s+(.+?)$', interface_config, re.MULTILINE)
			if desc_match:
				interface["description"] = desc_match.group(1).strip()
			
			# Extract IP address
			ip_match = re.search(r'ip address\s+(\S+)\s+(\S+)', interface_config)
			if ip_match:
				interface["ip_address"] = ip_match.group(1)
				interface["subnet_mask"] = ip_match.group(2)
			
			# Check if shutdown
			if re.search(r'shutdown', interface_config, re.MULTILINE):
				interface["enabled"] = False
			
			# Extract VRF
			vrf_match = re.search(r'ip vrf forwarding\s+(\S+)', interface_config)
			if vrf_match:
				interface["vrf"] = vrf_match.group(1)
				
			interfaces.append(interface)
		
		return interfaces
	
	def extract_acls(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract ACLs from Cisco IOS configuration."""
		acls = []
		
		# Find standard and extended ACLs
		acl_blocks = re.findall(
			r'^(ip access-list\s+\S+\s+\S+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for acl_header, acl_body in acl_blocks:
			acl_name_match = re.search(r'ip access-list\s+(\S+)\s+(\S+)', acl_header)
			if acl_name_match:
				acl_type = acl_name_match.group(1)
				acl_name = acl_name_match.group(2)
				
				rules = []
				for line in acl_body.strip().split('\n'):
					if line.strip() and not line.strip().startswith('!'):
						rules.append(line.strip())
				
				acls.append({
					"name": acl_name,
					"type": acl_type,
					"rules": rules
				})
		
		return acls
	
	def extract_vrfs(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract VRF configurations from Cisco IOS."""
		vrfs = []
		
		# Find VRF definitions
		vrf_blocks = re.findall(
			r'^ip vrf\s+(\S+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for vrf_name, vrf_config in vrf_blocks:
			vrf = {
				"name": vrf_name.strip(),
				"rd": "",
				"route_targets": [],
				"interfaces": []
			}
			
			# Extract route distinguisher
			rd_match = re.search(r'rd\s+(\S+)', vrf_config)
			if rd_match:
				vrf["rd"] = rd_match.group(1)
			
			# Extract route targets
			rt_exports = re.findall(r'route-target\s+export\s+(\S+)', vrf_config)
			rt_imports = re.findall(r'route-target\s+import\s+(\S+)', vrf_config)
			
			for rt in rt_exports:
				vrf["route_targets"].append({"type": "export", "value": rt})
			
			for rt in rt_imports:
				vrf["route_targets"].append({"type": "import", "value": rt})
			
			# Find interfaces in this VRF
			for interface in self.extract_interfaces(config_text):
				if interface["vrf"] == vrf_name:
					vrf["interfaces"].append(interface["name"])
			
			vrfs.append(vrf)
		
		return vrfs
	
	def extract_routing(self, config_text: str) -> Dict[str, Any]:
		"""Extract routing information from Cisco IOS configuration."""
		routing = {
			"static_routes": [],
			"ospf": {
				"enabled": False,
				"process_id": "",
				"router_id": "",
				"networks": []
			},
			"bgp": {
				"enabled": False,
				"as_number": "",
				"router_id": "",
				"neighbors": []
			}
		}
		
		# Extract static routes
		static_routes = re.findall(r'ip route\s+(\S+)\s+(\S+)\s+(\S+)', config_text)
		for network, mask, next_hop in static_routes:
			routing["static_routes"].append({
				"network": network,
				"mask": mask,
				"next_hop": next_hop
			})
		
		# Extract OSPF configuration
		ospf_match = re.search(
			r'^router ospf\s+(\d+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		if ospf_match:
			routing["ospf"]["enabled"] = True
			routing["ospf"]["process_id"] = ospf_match.group(1)
			ospf_config = ospf_match.group(2)
			
			# Extract router-id
			router_id_match = re.search(r'router-id\s+(\S+)', ospf_config)
			if router_id_match:
				routing["ospf"]["router_id"] = router_id_match.group(1)
			
			# Extract networks
			network_matches = re.findall(r'network\s+(\S+)\s+(\S+)\s+area\s+(\S+)', ospf_config)
			for network, wildcard, area in network_matches:
				routing["ospf"]["networks"].append({
					"network": network,
					"wildcard": wildcard,
					"area": area
				})
		
		# Extract BGP configuration
		bgp_match = re.search(
			r'^router bgp\s+(\d+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		if bgp_match:
			routing["bgp"]["enabled"] = True
			routing["bgp"]["as_number"] = bgp_match.group(1)
			bgp_config = bgp_match.group(2)
			
			# Extract router-id
			router_id_match = re.search(r'bgp router-id\s+(\S+)', bgp_config)
			if router_id_match:
				routing["bgp"]["router_id"] = router_id_match.group(1)
			
			# Extract neighbors
			neighbor_matches = re.findall(r'neighbor\s+(\S+)\s+remote-as\s+(\S+)', bgp_config)
			for neighbor, remote_as in neighbor_matches:
				routing["bgp"]["neighbors"].append({
					"ip": neighbor,
					"remote_as": remote_as
				})
		
		return routing


class CiscoASAParser(Parser):
	"""Parser for Cisco ASA Firewall devices."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""Parse Cisco ASA configuration."""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid Cisco ASA configuration.")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "cisco_asa",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text),
			"acls": self.extract_acls(config_text),
			"network_objects": self.extract_network_objects(config_text),
			"nat_rules": self.extract_nat_rules(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a Cisco ASA device."""
		asa_indicators = [
			r'ASA Version',
			r'access-list.*extended',
			r'class-map',
			r'policy-map',
			r'nat\s+\(\S+,\S+\)'
		]
		
		for indicator in asa_indicators:
			if re.search(indicator, config_text, re.IGNORECASE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from Cisco ASA configuration."""
		hostname_match = re.search(r'^hostname\s+(.+)$', config_text, re.MULTILINE)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interfaces from ASA configuration."""
		# Similar to IOS but with ASA-specific details
		# Implementation would be device-specific
		return []
	
	def extract_acls(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract ACLs from ASA configuration."""
		# ASA-specific ACL extraction
		return []
	
	def extract_network_objects(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract network objects from ASA configuration."""
		network_objects = []
		
		# Find object network definitions
		object_blocks = re.findall(
			r'^object network\s+(\S+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for object_name, object_config in object_blocks:
			network_object = {
				"name": object_name.strip(),
				"type": "network",
				"value": "",
				"description": ""
			}
			
			# Extract host or subnet
			host_match = re.search(r'host\s+(\S+)', object_config)
			subnet_match = re.search(r'subnet\s+(\S+)\s+(\S+)', object_config)
			desc_match = re.search(r'description\s+(.+?)$', object_config, re.MULTILINE)
			
			if host_match:
				network_object["value"] = f"host {host_match.group(1)}"
			elif subnet_match:
				network_object["value"] = f"subnet {subnet_match.group(1)} {subnet_match.group(2)}"
			
			if desc_match:
				network_object["description"] = desc_match.group(1).strip()
			
			network_objects.append(network_object)
		
		return network_objects
	
	def extract_nat_rules(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract NAT rules from ASA configuration."""
		nat_rules = []
		
		# Find NAT rule definitions
		nat_matches = re.findall(
			r'nat\s+\((\S+),(\S+)\)\s+(\S+)\s+(.+?)$', 
			config_text, 
			re.MULTILINE
		)
		
		for src_interface, dst_interface, nat_type, nat_config in nat_matches:
			nat_rule = {
				"source_interface": src_interface,
				"destination_interface": dst_interface,
				"type": nat_type,
				"config": nat_config.strip()
			}
			
			nat_rules.append(nat_rule)
		
		return nat_rules


class CiscoNexusParser(Parser):
	"""Parser for Cisco Nexus data center switches."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""Parse Cisco Nexus configuration."""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid Cisco Nexus configuration.")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "cisco_nexus",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text),
			"vlans": self.extract_vlans(config_text),
			"vpc": self.extract_vpc(config_text),
			"vdc": self.extract_vdc(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a Cisco Nexus device."""
		nexus_indicators = [
			r'feature\s+',
			r'vdc\s+',
			r'vpc domain',
			r'interface Ethernet\d+/\d+',
			r'interface port-channel'
		]
		
		for indicator in nexus_indicators:
			if re.search(indicator, config_text, re.IGNORECASE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from Cisco Nexus configuration."""
		hostname_match = re.search(r'^hostname\s+(.+)$', config_text, re.MULTILINE)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interface information from Nexus configuration."""
		# Nexus-specific interface extraction
		# Would include different interface types and Nexus-specific parameters
		return []
	
	def extract_vlans(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract VLAN information from Nexus configuration."""
		vlans = []
		
		# Find VLAN definitions
		vlan_blocks = re.findall(
			r'^vlan\s+(\d+)$\s+(.+?)(?=^!|^vlan\s+\d+|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for vlan_id, vlan_config in vlan_blocks:
			vlan = {
				"id": vlan_id.strip(),
				"name": "",
				"state": "active"
			}
			
			# Extract VLAN name
			name_match = re.search(r'name\s+(.+?)$', vlan_config, re.MULTILINE)
			if name_match:
				vlan["name"] = name_match.group(1).strip()
			
			# Extract VLAN state
			state_match = re.search(r'state\s+(\S+)', vlan_config)
			if state_match:
				vlan["state"] = state_match.group(1)
			
			vlans.append(vlan)
		
		return vlans
	
	def extract_vpc(self, config_text: str) -> Dict[str, Any]:
		"""Extract Virtual Port Channel (vPC) information from Nexus configuration."""
		vpc = {
			"domain_id": "",
			"peer_keepalive": "",
			"peer_gateway": False,
			"port_channels": []
		}
		
		# Extract vPC domain
		vpc_domain_match = re.search(
			r'^vpc domain\s+(\d+)$\s+(.+?)(?=^!|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		if vpc_domain_match:
			vpc["domain_id"] = vpc_domain_match.group(1)
			vpc_config = vpc_domain_match.group(2)
			
			# Extract peer-keepalive
			keepalive_match = re.search(r'peer-keepalive destination\s+(\S+)', vpc_config)
			if keepalive_match:
				vpc["peer_keepalive"] = keepalive_match.group(1)
			
			# Check for peer-gateway
			if re.search(r'peer-gateway', vpc_config):
				vpc["peer_gateway"] = True
		
		# Find port-channels with vPC configuration
		po_blocks = re.findall(
			r'^interface port-channel(\d+)$\s+(.+?)(?=^interface|\Z)', 
			config_text, 
			re.MULTILINE | re.DOTALL
		)
		
		for po_id, po_config in po_blocks:
			vpc_match = re.search(r'vpc\s+(\d+)', po_config)
			if vpc_match:
				vpc_id = vpc_match.group(1)
				vpc["port_channels"].append({
					"port_channel_id": po_id,
					"vpc_id": vpc_id
				})
		
		return vpc
	
	def extract_vdc(self, config_text: str) -> Dict[str, Any]:
		"""Extract Virtual Device Context (VDC) information from Nexus configuration."""
		vdc = {
			"name": "",
			"id": "",
			"status": "",
			"resource_limits": {}
		}
		
		# Extract VDC configuration
		# This would be specific to Nexus devices with VDC support
		# and would vary based on the Nexus model and NX-OS version
		
		return vdc 