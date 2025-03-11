"""
Parser for Juniper network devices.

This module contains the parser implementation for Juniper JunOS devices.
"""

import re
from typing import Dict, Any, List
from .base import Parser


class JuniperJunOSParser(Parser):
	"""Parser for Juniper JunOS devices."""
	
	def parse(self, config_text: str) -> Dict[str, Any]:
		"""
		Parse JunOS configuration.
		
		Args:
			config_text (str): The raw JunOS configuration text.
			
		Returns:
			Dict[str, Any]: Structured configuration data.
			
		Raises:
			ValueError: If the configuration is not valid JunOS.
		"""
		if not self.detect_device_type(config_text):
			raise ValueError("Not a valid JunOS configuration.")
		
		hostname = self.extract_hostname(config_text)
		
		return {
			"device_type": "junos",
			"hostname": hostname,
			"interfaces": self.extract_interfaces(config_text),
			"routing_instances": self.extract_routing_instances(config_text),
			"security_policies": self.extract_security_policies(config_text),
			"routing": self.extract_routing(config_text)
		}
	
	def detect_device_type(self, config_text: str) -> bool:
		"""Check if the configuration is from a Juniper JunOS device."""
		junos_indicators = [
			r'system\s+{\s+host-name\s+',
			r'interfaces\s+{\s+',
			r'protocols\s+{\s+',
			r'routing-options\s+{\s+',
			r'policy-options\s+{\s+',
			r'security\s+{\s+',
			r'version\s+\d+\.\d+[A-Z]\d+'
		]
		
		for indicator in junos_indicators:
			if re.search(indicator, config_text, re.MULTILINE):
				return True
		
		return False
	
	def extract_hostname(self, config_text: str) -> str:
		"""Extract hostname from JunOS configuration."""
		hostname_match = re.search(r'system\s+{\s+host-name\s+([^;]+);', config_text, re.DOTALL)
		if hostname_match:
			return hostname_match.group(1).strip()
		return ""
	
	def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract interface configurations from JunOS."""
		interfaces = []
		
		# Find interface configurations
		interface_section_match = re.search(r'interfaces\s+{(.*?)}', config_text, re.DOTALL)
		if not interface_section_match:
			return interfaces
			
		interface_section = interface_section_match.group(1)
		
		# Find each interface
		interface_blocks = re.findall(r'(\S+)\s+{(.*?)}', interface_section, re.DOTALL)
		
		for interface_name, interface_config in interface_blocks:
			# Skip if this doesn't look like an interface
			if interface_name in ['apply-groups', 'traceoptions']:
				continue
				
			interface = {
				"name": interface_name.strip(),
				"description": "",
				"units": [],
				"enabled": True
			}
			
			# Extract description
			desc_match = re.search(r'description\s+"([^"]+)"', interface_config)
			if desc_match:
				interface["description"] = desc_match.group(1)
			
			# Check if disabled
			if re.search(r'disable;', interface_config):
				interface["enabled"] = False
			
			# Extract units
			unit_blocks = re.findall(r'unit\s+(\d+)\s+{(.*?)}', interface_config, re.DOTALL)
			for unit_id, unit_config in unit_blocks:
				unit = {
					"id": unit_id.strip(),
					"description": "",
					"family": {
						"inet": {
							"addresses": []
						},
						"inet6": {
							"addresses": []
						}
					},
					"vlan_id": None
				}
				
				# Extract unit description
				unit_desc_match = re.search(r'description\s+"([^"]+)"', unit_config)
				if unit_desc_match:
					unit["description"] = unit_desc_match.group(1)
				
				# Extract VLAN ID
				vlan_id_match = re.search(r'vlan-id\s+(\d+)', unit_config)
				if vlan_id_match:
					unit["vlan_id"] = vlan_id_match.group(1)
				
				# Extract IPv4 addresses
				family_inet_match = re.search(r'family\s+inet\s+{(.*?)}', unit_config, re.DOTALL)
				if family_inet_match:
					family_inet = family_inet_match.group(1)
					address_matches = re.findall(r'address\s+([^;]+);', family_inet)
					for addr in address_matches:
						unit["family"]["inet"]["addresses"].append(addr.strip())
				
				# Extract IPv6 addresses
				family_inet6_match = re.search(r'family\s+inet6\s+{(.*?)}', unit_config, re.DOTALL)
				if family_inet6_match:
					family_inet6 = family_inet6_match.group(1)
					address_matches = re.findall(r'address\s+([^;]+);', family_inet6)
					for addr in address_matches:
						unit["family"]["inet6"]["addresses"].append(addr.strip())
				
				interface["units"].append(unit)
			
			interfaces.append(interface)
		
		return interfaces
	
	def extract_routing_instances(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract routing instance configurations from JunOS."""
		routing_instances = []
		
		# Find routing-instances section
		ri_section_match = re.search(r'routing-instances\s+{(.*?)}', config_text, re.DOTALL)
		if not ri_section_match:
			return routing_instances
			
		ri_section = ri_section_match.group(1)
		
		# Find each routing instance
		ri_blocks = re.findall(r'(\S+)\s+{(.*?instance-type\s+([^;]+);.*?)}', ri_section, re.DOTALL)
		
		for ri_name, ri_config, ri_type in ri_blocks:
			ri = {
				"name": ri_name.strip(),
				"type": ri_type.strip(),
				"description": "",
				"interfaces": [],
				"route_distinguisher": "",
				"vrf_target": ""
			}
			
			# Extract description
			desc_match = re.search(r'description\s+"([^"]+)"', ri_config)
			if desc_match:
				ri["description"] = desc_match.group(1)
			
			# Extract interfaces
			interface_matches = re.findall(r'interface\s+([^;]+);', ri_config)
			for intf in interface_matches:
				ri["interfaces"].append(intf.strip())
			
			# Extract VRF properties if applicable
			if ri_type.strip() in ['vrf', 'virtual-router']:
				# Extract route distinguisher
				rd_match = re.search(r'route-distinguisher\s+([^;]+);', ri_config)
				if rd_match:
					ri["route_distinguisher"] = rd_match.group(1).strip()
				
				# Extract VRF target
				vrf_target_match = re.search(r'vrf-target\s+([^;]+);', ri_config)
				if vrf_target_match:
					ri["vrf_target"] = vrf_target_match.group(1).strip()
			
			routing_instances.append(ri)
		
		return routing_instances
	
	def extract_security_policies(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract security policies from JunOS configuration."""
		policies = []
		
		# Find security policies section
		security_match = re.search(r'security\s+{.*?policies\s+{(.*?)}', config_text, re.DOTALL)
		if not security_match:
			return policies
			
		policies_section = security_match.group(1)
		
		# Find from-zone/to-zone sections
		zone_blocks = re.findall(r'from-zone\s+(\S+)\s+to-zone\s+(\S+)\s+{(.*?)}', policies_section, re.DOTALL)
		
		for from_zone, to_zone, zone_config in zone_blocks:
			# Find each policy
			policy_blocks = re.findall(r'policy\s+(\S+)\s+{(.*?)}', zone_config, re.DOTALL)
			
			for policy_name, policy_config in policy_blocks:
				policy = {
					"name": policy_name.strip(),
					"from_zone": from_zone.strip(),
					"to_zone": to_zone.strip(),
					"match": {
						"source_address": [],
						"destination_address": [],
						"application": []
					},
					"then": {
						"action": ""
					},
					"description": ""
				}
				
				# Extract match criteria
				match_section = re.search(r'match\s+{(.*?)}', policy_config, re.DOTALL)
				if match_section:
					match_config = match_section.group(1)
					
					# Source addresses
					src_addr_matches = re.findall(r'source-address\s+([^;]+);', match_config)
					for src in src_addr_matches:
						policy["match"]["source_address"].append(src.strip())
					
					# Destination addresses
					dst_addr_matches = re.findall(r'destination-address\s+([^;]+);', match_config)
					for dst in dst_addr_matches:
						policy["match"]["destination_address"].append(dst.strip())
					
					# Applications
					app_matches = re.findall(r'application\s+([^;]+);', match_config)
					for app in app_matches:
						policy["match"]["application"].append(app.strip())
				
				# Extract actions
				then_section = re.search(r'then\s+{(.*?)}', policy_config, re.DOTALL)
				if then_section:
					then_config = then_section.group(1)
					
					# Determine action (permit, deny, reject)
					if re.search(r'permit;', then_config):
						policy["then"]["action"] = "permit"
					elif re.search(r'deny;', then_config):
						policy["then"]["action"] = "deny"
					elif re.search(r'reject;', then_config):
						policy["then"]["action"] = "reject"
				
				# Extract description
				desc_match = re.search(r'description\s+"([^"]+)"', policy_config)
				if desc_match:
					policy["description"] = desc_match.group(1)
				
				policies.append(policy)
		
		return policies
	
	def extract_routing(self, config_text: str) -> Dict[str, Any]:
		"""Extract routing configurations from JunOS."""
		routing = {
			"static_routes": [],
			"bgp": {
				"as_number": "",
				"neighbors": []
			},
			"ospf": {
				"areas": []
			}
		}
		
		# Extract static routes
		routing_options_match = re.search(r'routing-options\s+{(.*?)}', config_text, re.DOTALL)
		if routing_options_match:
			routing_options = routing_options_match.group(1)
			
			# AS number for BGP
			as_match = re.search(r'autonomous-system\s+(\d+)', routing_options)
			if as_match:
				routing["bgp"]["as_number"] = as_match.group(1).strip()
			
			# Static routes
			static_section = re.search(r'static\s+{(.*?)}', routing_options, re.DOTALL)
			if static_section:
				static_config = static_section.group(1)
				route_matches = re.findall(r'route\s+([^{]+){(.*?)}', static_config, re.DOTALL)
				
				for prefix, route_config in route_matches:
					route = {
						"prefix": prefix.strip(),
						"next_hop": "",
						"preference": "5"  # Default
					}
					
					# Extract next-hop
					next_hop_match = re.search(r'next-hop\s+([^;]+);', route_config)
					if next_hop_match:
						route["next_hop"] = next_hop_match.group(1).strip()
					
					# Extract preference
					pref_match = re.search(r'preference\s+(\d+)', route_config)
					if pref_match:
						route["preference"] = pref_match.group(1).strip()
					
					routing["static_routes"].append(route)
		
		# Extract BGP configuration
		protocols_match = re.search(r'protocols\s+{(.*?)}', config_text, re.DOTALL)
		if protocols_match:
			protocols = protocols_match.group(1)
			
			# BGP configuration
			bgp_section = re.search(r'bgp\s+{(.*?)}', protocols, re.DOTALL)
			if bgp_section:
				bgp_config = bgp_section.group(1)
				
				# BGP neighbors
				group_blocks = re.findall(r'group\s+(\S+)\s+{(.*?)}', bgp_config, re.DOTALL)
				
				for group_name, group_config in group_blocks:
					# Extract neighbors
					neighbor_matches = re.findall(r'neighbor\s+([^{;]+)(?:{(.*?)}|;)', group_config, re.DOTALL)
					
					for neighbor_addr, neighbor_config in neighbor_matches:
						neighbor = {
							"address": neighbor_addr.strip(),
							"peer_as": "",
							"description": "",
							"group": group_name.strip()
						}
						
						# Extract peer AS
						if len(neighbor_config) > 0:
							peer_as_match = re.search(r'peer-as\s+(\d+)', neighbor_config)
							if peer_as_match:
								neighbor["peer_as"] = peer_as_match.group(1).strip()
							
							# Extract description
							desc_match = re.search(r'description\s+"([^"]+)"', neighbor_config)
							if desc_match:
								neighbor["description"] = desc_match.group(1)
						
						# Check for peer-as at group level if not found at neighbor level
						if not neighbor["peer_as"]:
							group_peer_as_match = re.search(r'peer-as\s+(\d+)', group_config)
							if group_peer_as_match:
								neighbor["peer_as"] = group_peer_as_match.group(1).strip()
						
						routing["bgp"]["neighbors"].append(neighbor)
			
			# OSPF configuration
			ospf_section = re.search(r'ospf\s+{(.*?)}', protocols, re.DOTALL)
			if ospf_section:
				ospf_config = ospf_section.group(1)
				
				# OSPF areas
				area_blocks = re.findall(r'area\s+([^{]+){(.*?)}', ospf_config, re.DOTALL)
				
				for area_id, area_config in area_blocks:
					area = {
						"id": area_id.strip(),
						"interfaces": []
					}
					
					# Extract interfaces
					interface_matches = re.findall(r'interface\s+([^{;]+)(?:{(.*?)}|;)', area_config, re.DOTALL)
					
					for intf_name, intf_config in interface_matches:
						interface = {
							"name": intf_name.strip(),
							"passive": False,
							"metric": ""
						}
						
						# Check if passive
						if len(intf_config) > 0 and re.search(r'passive;', intf_config):
							interface["passive"] = True
						
						# Extract metric
						if len(intf_config) > 0:
							metric_match = re.search(r'metric\s+(\d+)', intf_config)
							if metric_match:
								interface["metric"] = metric_match.group(1).strip()
						
						area["interfaces"].append(interface)
					
					routing["ospf"]["areas"].append(area)
		
		return routing
	
	def extract_acls(self, config_text: str) -> List[Dict[str, Any]]:
		"""Extract Access Control Lists (firewall filters) from JunOS configuration."""
		acls = []
		
		# Find firewall section
		firewall_match = re.search(r'firewall\s+{(.*?)}', config_text, re.DOTALL)
		if not firewall_match:
			return acls
			
		firewall_section = firewall_match.group(1)
		
		# Find filter (ACL) blocks
		filter_blocks = re.findall(r'filter\s+(\S+)\s+{(.*?)}', firewall_section, re.DOTALL)
		
		for filter_name, filter_config in filter_blocks:
			acl = {
				"name": filter_name.strip(),
				"family": "inet",  # Default to IPv4
				"terms": []
			}
			
			# Determine family (inet/inet6)
			if re.search(r'family\s+inet6', filter_config):
				acl["family"] = "inet6"
			
			# Extract terms
			term_blocks = re.findall(r'term\s+(\S+)\s+{(.*?)}', filter_config, re.DOTALL)
			
			for term_name, term_config in term_blocks:
				term = {
					"name": term_name.strip(),
					"from": {},
					"then": {}
				}
				
				# Extract from conditions
				from_section = re.search(r'from\s+{(.*?)}', term_config, re.DOTALL)
				if from_section:
					from_config = from_section.group(1)
					
					# Common match criteria
					match_criteria = [
						("source-address", "source_address"),
						("destination-address", "destination_address"),
						("source-port", "source_port"),
						("destination-port", "destination_port"),
						("protocol", "protocol")
					]
					
					for junos_name, dict_name in match_criteria:
						matches = re.findall(fr'{junos_name}\s+([^;]+);', from_config)
						if matches:
							term["from"][dict_name] = [m.strip() for m in matches]
				
				# Extract then actions
				then_section = re.search(r'then\s+{(.*?)}', term_config, re.DOTALL)
				if then_section:
					then_config = then_section.group(1)
					
					# Determine action
					if re.search(r'accept;', then_config):
						term["then"]["action"] = "accept"
					elif re.search(r'discard;', then_config):
						term["then"]["action"] = "discard"
					elif re.search(r'reject;', then_config):
						term["then"]["action"] = "reject"
					
					# Check for counter
					counter_match = re.search(r'count\s+([^;]+);', then_config)
					if counter_match:
						term["then"]["counter"] = counter_match.group(1).strip()
				
				acl["terms"].append(term)
			
			acls.append(acl)
		
		return acls
	
	def extract_vrfs(self, config_text: str) -> List[Dict[str, Any]]:
		"""
		Extract VRF information (implemented as routing-instances in JunOS).
		This is an alias for extract_routing_instances with filtering for VRF type.
		"""
		all_instances = self.extract_routing_instances(config_text)
		return [ri for ri in all_instances if ri["type"] in ["vrf", "virtual-router"]] 