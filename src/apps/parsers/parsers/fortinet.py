"""
Parsers for Fortinet network devices.

This module contains parser implementations for Fortinet device types:
- FortiGate (Firewalls)
- FortiSwitch (Switches)
"""

import re
from typing import Dict, Any, List
from .base import Parser


class FortiGateParser(Parser):
	"""Parser for FortiGate firewall devices."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""
		Parse FortiGate configuration.
		
		Args:
			config_text (str): The raw FortiGate configuration text.
			
		Returns:
			Dict[str, Any]: Structured configuration data.
			
		Raises:
			ValueError: If the configuration is not valid FortiGate.
		"""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid FortiGate configuration.")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "fortigate",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text),
			"policies": self.extract_policies(config_text),
			"address_objects": self.extract_address_objects(config_text),
			"service_objects": self.extract_service_objects(config_text),
			"vpn": self.extract_vpn(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a FortiGate device."""
		fortigate_indicators = [
			r'config\s+system\s+global',
			r'config\s+firewall\s+policy',
			r'config\s+vpn\s+ipsec\s+phase1-interface',
			r'set\s+vdom\s+',
			r'config\s+firewall\s+address'
		]
		
		for indicator in fortigate_indicators:
			if re.search(indicator, config_text, re.IGNORECASE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from FortiGate configuration."""
		hostname_match = re.search(r'set\s+hostname\s+"?([^"\r\n]+)"?', config_text)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interface configurations from FortiGate."""
		interfaces = []
		
		# Find interface configurations
		interface_blocks = re.findall(
			r'config\s+system\s+interface\s+.*?edit\s+"([^"]+)"(.*?)next\s+.*?end',
			config_text,
			re.DOTALL
		)
		
		for interface_name, interface_config in interface_blocks:
			interface = {
				"name": interface_name.strip(),
				"ip": "",
				"netmask": "",
				"vdom": "root",
				"type": "physical",
				"description": "",
				"enabled": True
			}
			
			# Extract IP
			ip_match = re.search(r'set\s+ip\s+(\S+)\s+(\S+)', interface_config)
			if ip_match:
				interface["ip"] = ip_match.group(1)
				interface["netmask"] = ip_match.group(2)
			
			# Extract VDOM
			vdom_match = re.search(r'set\s+vdom\s+"?([^"\r\n]+)"?', interface_config)
			if vdom_match:
				interface["vdom"] = vdom_match.group(1)
			
			# Extract interface type
			type_match = re.search(r'set\s+type\s+(\S+)', interface_config)
			if type_match:
				interface["type"] = type_match.group(1)
			
			# Extract description
			desc_match = re.search(r'set\s+description\s+"([^"]+)"', interface_config)
			if desc_match:
				interface["description"] = desc_match.group(1)
			
			# Check status
			status_match = re.search(r'set\s+status\s+(\S+)', interface_config)
			if status_match and status_match.group(1).lower() == "down":
				interface["enabled"] = False
			
			interfaces.append(interface)
		
		return interfaces
	
	def extract_policies(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract firewall policies from FortiGate configuration."""
		policies = []
		
		# Find policy configurations
		policy_blocks = re.findall(
			r'edit\s+(\d+)(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for policy_id, policy_config in policy_blocks:
			# Skip if this doesn't look like a firewall policy
			if not re.search(r'set\s+action\s+', policy_config):
				continue
				
			policy = {
				"id": policy_id.strip(),
				"name": "",
				"srcintf": [],
				"dstintf": [],
				"srcaddr": [],
				"dstaddr": [],
				"service": [],
				"action": "deny",
				"status": "enabled",
				"nat": False
			}
			
			# Extract policy name
			name_match = re.search(r'set\s+name\s+"([^"]+)"', policy_config)
			if name_match:
				policy["name"] = name_match.group(1)
			
			# Extract source interfaces
			srcintf_match = re.search(r'set\s+srcintf\s+(.+?)$', policy_config, re.MULTILINE)
			if srcintf_match:
				srcintf_str = srcintf_match.group(1).strip()
				srcintf_list = re.findall(r'"([^"]+)"', srcintf_str)
				policy["srcintf"] = srcintf_list
			
			# Extract destination interfaces
			dstintf_match = re.search(r'set\s+dstintf\s+(.+?)$', policy_config, re.MULTILINE)
			if dstintf_match:
				dstintf_str = dstintf_match.group(1).strip()
				dstintf_list = re.findall(r'"([^"]+)"', dstintf_str)
				policy["dstintf"] = dstintf_list
			
			# Extract source addresses
			srcaddr_match = re.search(r'set\s+srcaddr\s+(.+?)$', policy_config, re.MULTILINE)
			if srcaddr_match:
				srcaddr_str = srcaddr_match.group(1).strip()
				srcaddr_list = re.findall(r'"([^"]+)"', srcaddr_str)
				policy["srcaddr"] = srcaddr_list
			
			# Extract destination addresses
			dstaddr_match = re.search(r'set\s+dstaddr\s+(.+?)$', policy_config, re.MULTILINE)
			if dstaddr_match:
				dstaddr_str = dstaddr_match.group(1).strip()
				dstaddr_list = re.findall(r'"([^"]+)"', dstaddr_str)
				policy["dstaddr"] = dstaddr_list
			
			# Extract services
			service_match = re.search(r'set\s+service\s+(.+?)$', policy_config, re.MULTILINE)
			if service_match:
				service_str = service_match.group(1).strip()
				service_list = re.findall(r'"([^"]+)"', service_str)
				policy["service"] = service_list
			
			# Extract action
			action_match = re.search(r'set\s+action\s+(\S+)', policy_config)
			if action_match:
				policy["action"] = action_match.group(1)
			
			# Check status
			status_match = re.search(r'set\s+status\s+(\S+)', policy_config)
			if status_match:
				policy["status"] = status_match.group(1)
			
			# Check NAT
			nat_match = re.search(r'set\s+nat\s+(\S+)', policy_config)
			if nat_match and nat_match.group(1) == "enable":
				policy["nat"] = True
			
			policies.append(policy)
		
		return policies
	
	def extract_address_objects(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract address objects from FortiGate configuration."""
		address_objects = []
		
		# Find address configurations
		address_blocks = re.findall(
			r'config\s+firewall\s+address.*?edit\s+"([^"]+)"(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for addr_name, addr_config in address_blocks:
			address = {
				"name": addr_name.strip(),
				"type": "ipmask",
				"subnet": "",
				"fqdn": "",
				"comment": ""
			}
			
			# Extract type
			type_match = re.search(r'set\s+type\s+(\S+)', addr_config)
			if type_match:
				address["type"] = type_match.group(1)
			
			# Extract subnet if type is ipmask
			if address["type"] == "ipmask":
				subnet_match = re.search(r'set\s+subnet\s+(\S+)\s+(\S+)', addr_config)
				if subnet_match:
					address["subnet"] = f"{subnet_match.group(1)}/{subnet_match.group(2)}"
			
			# Extract FQDN if type is fqdn
			if address["type"] == "fqdn":
				fqdn_match = re.search(r'set\s+fqdn\s+"([^"]+)"', addr_config)
				if fqdn_match:
					address["fqdn"] = fqdn_match.group(1)
			
			# Extract comment
			comment_match = re.search(r'set\s+comment\s+"([^"]+)"', addr_config)
			if comment_match:
				address["comment"] = comment_match.group(1)
			
			address_objects.append(address)
		
		return address_objects
	
	def extract_service_objects(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract service objects from FortiGate configuration."""
		service_objects = []
		
		# Find service configurations
		service_blocks = re.findall(
			r'config\s+firewall\s+service\s+custom.*?edit\s+"([^"]+)"(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for svc_name, svc_config in service_blocks:
			service = {
				"name": svc_name.strip(),
				"protocol": "",
				"ports": [],
				"comment": ""
			}
			
			# Extract protocol
			protocol_match = re.search(r'set\s+protocol\s+(\S+)', svc_config)
			if protocol_match:
				service["protocol"] = protocol_match.group(1)
			
			# Extract ports for TCP/UDP
			if service["protocol"] in ["TCP", "UDP", "SCTP"]:
				proto_lower = service["protocol"].lower()
				port_match = re.search(fr'set\s+{proto_lower}-portrange\s+(.+?)$', svc_config, re.MULTILINE)
				if port_match:
					port_ranges = port_match.group(1).strip().split(" ")
					service["ports"] = port_ranges
			
			# Extract comment
			comment_match = re.search(r'set\s+comment\s+"([^"]+)"', svc_config)
			if comment_match:
				service["comment"] = comment_match.group(1)
			
			service_objects.append(service)
		
		return service_objects
	
	def extract_vpn(self, config_text: str) -> Dict[str, Any]:
		"""Extract VPN configurations from FortiGate."""
		vpn = {
			"ipsec": [],
			"ssl": {
				"enabled": False,
				"portals": []
			}
		}
		
		# Find IPsec VPN phase1 configurations
		phase1_blocks = re.findall(
			r'config\s+vpn\s+ipsec\s+phase1-interface.*?edit\s+"([^"]+)"(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for vpn_name, vpn_config in phase1_blocks:
			ipsec_vpn = {
				"name": vpn_name.strip(),
				"interface": "",
				"remote_gw": "",
				"mode": "main",
				"proposal": [],
				"dhgrp": [],
				"psk": False,
				"certificate": False,
				"phase2": []
			}
			
			# Extract interface
			intf_match = re.search(r'set\s+interface\s+"([^"]+)"', vpn_config)
			if intf_match:
				ipsec_vpn["interface"] = intf_match.group(1)
			
			# Extract remote gateway
			gw_match = re.search(r'set\s+remote-gw\s+(\S+)', vpn_config)
			if gw_match:
				ipsec_vpn["remote_gw"] = gw_match.group(1)
			
			# Extract mode
			mode_match = re.search(r'set\s+mode\s+(\S+)', vpn_config)
			if mode_match:
				ipsec_vpn["mode"] = mode_match.group(1)
			
			# Extract proposals
			proposal_match = re.search(r'set\s+proposal\s+(.+?)$', vpn_config, re.MULTILINE)
			if proposal_match:
				proposals = proposal_match.group(1).strip().split(" ")
				ipsec_vpn["proposal"] = proposals
			
			# Extract DH groups
			dhgrp_match = re.search(r'set\s+dhgrp\s+(.+?)$', vpn_config, re.MULTILINE)
			if dhgrp_match:
				dhgrps = dhgrp_match.group(1).strip().split(" ")
				ipsec_vpn["dhgrp"] = dhgrps
			
			# Check authentication method
			if re.search(r'set\s+psksecret', vpn_config):
				ipsec_vpn["psk"] = True
			if re.search(r'set\s+certificate', vpn_config):
				ipsec_vpn["certificate"] = True
			
			# Find associated phase2 configurations
			phase2_blocks = re.findall(
				fr'config\s+vpn\s+ipsec\s+phase2-interface.*?edit\s+"([^"]+)".*?set\s+phase1name\s+"{vpn_name}"(.*?)next',
				config_text,
				re.DOTALL
			)
			
			for phase2_name, phase2_config in phase2_blocks:
				phase2 = {
					"name": phase2_name.strip(),
					"proposal": [],
					"src_subnet": [],
					"dst_subnet": []
				}
				
				# Extract proposals
				proposal_match = re.search(r'set\s+proposal\s+(.+?)$', phase2_config, re.MULTILINE)
				if proposal_match:
					proposals = proposal_match.group(1).strip().split(" ")
					phase2["proposal"] = proposals
				
				# Extract source subnet
				src_match = re.search(r'set\s+src-subnet\s+(\S+)\s+(\S+)', phase2_config)
				if src_match:
					phase2["src_subnet"].append(f"{src_match.group(1)}/{src_match.group(2)}")
				
				# Extract destination subnet
				dst_match = re.search(r'set\s+dst-subnet\s+(\S+)\s+(\S+)', phase2_config)
				if dst_match:
					phase2["dst_subnet"].append(f"{dst_match.group(1)}/{dst_match.group(2)}")
				
				ipsec_vpn["phase2"].append(phase2)
			
			vpn["ipsec"].append(ipsec_vpn)
		
		return vpn


class FortiSwitchParser(Parser):
	"""Parser for FortiSwitch devices."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""Parse FortiSwitch configuration."""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid FortiSwitch configuration.")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "fortiswitch",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text),
			"vlans": self.extract_vlans(config_text),
			"switch_ports": self.extract_switch_ports(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a FortiSwitch device."""
		fortiswitch_indicators = [
			r'config\s+switch\s+vlan',
			r'config\s+switch\s+physical-port',
			r'config-version=[A-Z\d]+-FGT_',
			r'FortiSwitch\s+\d+',
			r'FortiOS'
		]
		
		for indicator in fortiswitch_indicators:
			if re.search(indicator, config_text, re.IGNORECASE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from FortiSwitch configuration."""
		hostname_match = re.search(r'set\s+hostname\s+"?([^"\r\n]+)"?', config_text)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interface configurations from FortiSwitch."""
		# Similar to FortiGate but with switch-specific details
		return []
	
	def extract_vlans(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract VLAN configurations from FortiSwitch."""
		vlans = []
		
		# Find VLAN configurations
		vlan_blocks = re.findall(
			r'config\s+switch\s+vlan.*?edit\s+(\d+)(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for vlan_id, vlan_config in vlan_blocks:
			vlan = {
				"id": vlan_id.strip(),
				"name": "",
				"description": ""
			}
			
			# Extract VLAN name
			name_match = re.search(r'set\s+name\s+"([^"]+)"', vlan_config)
			if name_match:
				vlan["name"] = name_match.group(1)
			
			# Extract description
			desc_match = re.search(r'set\s+description\s+"([^"]+)"', vlan_config)
			if desc_match:
				vlan["description"] = desc_match.group(1)
			
			vlans.append(vlan)
		
		return vlans
	
	def extract_switch_ports(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract switch port configurations from FortiSwitch."""
		switch_ports = []
		
		# Find switch port configurations
		port_blocks = re.findall(
			r'config\s+switch\s+physical-port.*?edit\s+"([^"]+)"(.*?)next',
			config_text,
			re.DOTALL
		)
		
		for port_name, port_config in port_blocks:
			port = {
				"name": port_name.strip(),
				"speed": "auto",
				"status": "up",
				"poe": False,
				"vlan": "",
				"description": ""
			}
			
			# Extract speed
			speed_match = re.search(r'set\s+speed\s+(\S+)', port_config)
			if speed_match:
				port["speed"] = speed_match.group(1)
			
			# Extract status
			status_match = re.search(r'set\s+status\s+(\S+)', port_config)
			if status_match:
				port["status"] = status_match.group(1)
			
			# Check PoE status
			poe_match = re.search(r'set\s+poe-status\s+(\S+)', port_config)
			if poe_match and poe_match.group(1) == "enable":
				port["poe"] = True
			
			# Extract VLAN
			vlan_match = re.search(r'set\s+vlan\s+"?(\d+)"?', port_config)
			if vlan_match:
				port["vlan"] = vlan_match.group(1)
			
			# Extract description
			desc_match = re.search(r'set\s+description\s+"([^"]+)"', port_config)
			if desc_match:
				port["description"] = desc_match.group(1)
			
			switch_ports.append(port)
		
		return switch_ports 