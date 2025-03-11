# Parser Usage Examples

This document provides practical examples of how to use the parser system.

## Basic Usage

### Using a Specific Parser Directly

```python
from apps.parsers.parsers.cisco import CiscoIOSParser

# Create parser instance
parser = CiscoIOSParser()

# Load a configuration file
with open('router_config.txt', 'r') as f:
    config_text = f.read()

# Check if this parser can handle the configuration
if parser.detect_device_type(config_text):
    # Parse the configuration
    parsed_data = parser.parse(config_text)
    
    # Access parsed data
    hostname = parsed_data['hostname']
    interfaces = parsed_data['interfaces']
    
    print(f"Device hostname: {hostname}")
    print(f"Number of interfaces: {len(interfaces)}")
else:
    print("This is not a Cisco IOS configuration.")
```

### Using the Parser Factory

```python
from apps.parsers.parsers.factory import ParserFactory

# Load a configuration file
with open('unknown_device_config.txt', 'r') as f:
    config_text = f.read()

# Let the factory detect the appropriate parser
parser = ParserFactory.get_parser(config_text)
if parser:
    # Parse the configuration
    parsed_data = parser.parse(config_text)
    
    # Access parsed data
    device_type = parsed_data['device_type']
    hostname = parsed_data['hostname']
    
    print(f"Detected device type: {device_type}")
    print(f"Device hostname: {hostname}")
else:
    print("No compatible parser found for this configuration.")
```

### Using in Django Views

```python
from django.views.generic import DetailView
from django.contrib import messages
from apps.parsers.models import DeviceFile

class DeviceFileDetailView(DetailView):
    model = DeviceFile
    template_name = 'parsers/devicefile_detail.html'
    
    def post(self, request, *args, **kwargs):
        """Handle POST requests to parse the file."""
        self.object = self.get_object()
        
        # Parse the file when requested
        if 'parse' in request.POST:
            success = self.object.parse_file()
            if success:
                messages.success(request, f"Successfully parsed {self.object.name}")
            else:
                messages.error(request, f"Error parsing {self.object.name}: {self.object.parse_errors}")
        
        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)
```

## Advanced Usage

### Extracting Specific Information

```python
from apps.parsers.parsers.cisco import CiscoIOSParser

parser = CiscoIOSParser()

with open('router_config.txt', 'r') as f:
    config_text = f.read()

# Extract only the interfaces
interfaces = parser.extract_interfaces(config_text)
for interface in interfaces:
    name = interface['name']
    ip = interface.get('ip_address', 'No IP')
    description = interface.get('description', 'No description')
    
    print(f"Interface: {name}, IP: {ip}, Description: {description}")

# Extract only ACLs
acls = parser.extract_acls(config_text)
for acl in acls:
    acl_number = acl['number']
    entry_count = len(acl['entries'])
    
    print(f"ACL: {acl_number}, Entries: {entry_count}")
```

### Implementing Batch Processing

```python
import os
from apps.parsers.parsers.factory import ParserFactory

def batch_process_configs(directory_path):
    """Process all configuration files in a directory."""
    results = []
    
    # Process each file in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.txt') or filename.endswith('.cfg'):
            file_path = os.path.join(directory_path, filename)
            
            with open(file_path, 'r') as f:
                config_text = f.read()
            
            # Get appropriate parser
            parser = ParserFactory.get_parser(config_text)
            if parser:
                try:
                    # Parse the configuration
                    parsed_data = parser.parse(config_text)
                    results.append({
                        'filename': filename,
                        'status': 'success',
                        'device_type': parsed_data['device_type'],
                        'hostname': parsed_data['hostname']
                    })
                except Exception as e:
                    results.append({
                        'filename': filename,
                        'status': 'error',
                        'error_message': str(e)
                    })
            else:
                results.append({
                    'filename': filename,
                    'status': 'error',
                    'error_message': 'No compatible parser found'
                })
    
    return results

# Example usage
results = batch_process_configs('/path/to/configs')
for result in results:
    if result['status'] == 'success':
        print(f"Processed {result['filename']}: {result['device_type']} - {result['hostname']}")
    else:
        print(f"Failed to process {result['filename']}: {result['error_message']}")
```

### Creating a Custom Parser for a Specific Format

Sometimes you might need a custom parser for a unique format or vendor. Here's how to create one:

```python
from apps.parsers.parsers.base import Parser
import re
from typing import Dict, Any, List

class CustomFormatParser(Parser):
    """Parser for a custom format."""
    
    def parse(self, config_text: str) -> Dict[str, Any]:
        """Parse custom format configuration."""
        if not self.detect_device_type(config_text):
            raise ValueError("Not a valid custom format configuration.")
        
        # Extract and structure the data
        return {
            "device_type": "custom-format",
            "hostname": self.extract_hostname(config_text),
            "interfaces": self.extract_interfaces(config_text),
            "custom_sections": self.extract_custom_sections(config_text)
        }
    
    def detect_device_type(self, config_text: str) -> bool:
        """Check if the configuration matches our custom format."""
        # Look for patterns specific to this format
        return "CUSTOM-FORMAT-HEADER" in config_text and "CONFIG-VERSION" in config_text
    
    def extract_hostname(self, config_text: str) -> str:
        """Extract hostname from custom format."""
        match = re.search(r'HOSTNAME:\s*(\S+)', config_text)
        if match:
            return match.group(1)
        return ""
    
    def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
        """Extract interface information from custom format."""
        interfaces = []
        
        # Find all interface sections
        interface_sections = re.findall(
            r'INTERFACE-BEGIN\s+(\S+)\s+(.*?)INTERFACE-END',
            config_text,
            re.DOTALL
        )
        
        for intf_name, intf_config in interface_sections:
            interface = {
                "name": intf_name,
                "ip_address": "",
                "subnet_mask": "",
                "description": ""
            }
            
            # Extract IP address
            ip_match = re.search(r'IP-ADDRESS:\s+(\S+)', intf_config)
            if ip_match:
                interface["ip_address"] = ip_match.group(1)
            
            # Extract subnet mask
            mask_match = re.search(r'SUBNET-MASK:\s+(\S+)', intf_config)
            if mask_match:
                interface["subnet_mask"] = mask_match.group(1)
            
            # Extract description
            desc_match = re.search(r'DESCRIPTION:\s+(.+?)$', intf_config, re.MULTILINE)
            if desc_match:
                interface["description"] = desc_match.group(1).strip()
            
            interfaces.append(interface)
        
        return interfaces
    
    def extract_custom_sections(self, config_text: str) -> Dict[str, Any]:
        """Extract custom sections specific to this format."""
        custom_data = {}
        
        # Example: Extract a custom section
        section_match = re.search(
            r'CUSTOM-SECTION-BEGIN\s+(.*?)CUSTOM-SECTION-END',
            config_text,
            re.DOTALL
        )
        
        if section_match:
            custom_data["section_content"] = section_match.group(1).strip()
        
        return custom_data

# Register with the factory
# In apps/parsers/parsers/factory.py:
# Add to ParserFactory._get_parser_classes() and get_parser_for_device_type()
```

## Error Handling

Always handle exceptions when parsing, as configuration files can have unexpected formats:

```python
from apps.parsers.parsers.factory import ParserFactory

with open('config.txt', 'r') as f:
    config_text = f.read()

try:
    parser = ParserFactory.get_parser(config_text)
    if parser:
        parsed_data = parser.parse(config_text)
        # Process parsed data
    else:
        # Handle unknown device type
        print("No parser available for this configuration")
except ValueError as e:
    # Handle parsing errors
    print(f"Error parsing configuration: {str(e)}")
except Exception as e:
    # Handle unexpected errors
    print(f"Unexpected error: {str(e)}") 