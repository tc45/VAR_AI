# Network Device Parsers

This document provides detailed information about the network device configuration parsers in the VarAI system.

## Overview

The parser system is designed to convert raw network device configurations into structured data that can be stored in the inventory and used for reporting. The system follows an object-oriented approach with a clear inheritance hierarchy:

- A base `Parser` abstract class defines the interface
- Device-specific parser implementations extend this class
- A factory class automatically selects the appropriate parser based on device type or configuration content

This architecture makes it easy to add support for new device types without modifying existing code.

## Base Parser Interface

The base parser is defined in `apps/parsers/parsers/base.py` and provides:

- Abstract methods that must be implemented by all parser subclasses
- Utility methods that have default implementations but can be overridden if needed

### Required Methods

All parser implementations must provide these methods:

```python
@abstractmethod
def parse(self, config_text: str) -> Dict[str, Any]:
    """
    Parse the device configuration text into a structured format.
    
    Args:
        config_text (str): The raw device configuration text
        
    Returns:
        Dict[str, Any]: Structured configuration data
        
    Raises:
        ValueError: If the configuration is invalid
    """
    pass

@abstractmethod
def detect_device_type(self, config_text: str) -> bool:
    """
    Determine if this parser can handle the given configuration text.
    
    Args:
        config_text (str): The raw device configuration text
        
    Returns:
        bool: True if this parser can handle the configuration, False otherwise
    """
    pass
```

### Optional Methods

The base parser also provides these methods with default implementations:

```python
def extract_hostname(self, config_text: str) -> str:
    """Extract the hostname from the configuration."""
    return ""

def extract_interfaces(self, config_text: str) -> List[Dict[str, Any]]:
    """Extract interface configurations."""
    return []

def extract_acls(self, config_text: str) -> List[Dict[str, Any]]:
    """Extract Access Control Lists."""
    return []

def extract_vrfs(self, config_text: str) -> List[Dict[str, Any]]:
    """Extract Virtual Routing and Forwarding data."""
    return []

def extract_routing(self, config_text: str) -> Dict[str, Any]:
    """Extract routing information."""
    return {}
```

## Implemented Parsers

The system includes parsers for these device types:

### Cisco Parsers

#### CiscoIOSParser

The Cisco IOS parser handles router and switch configurations for Cisco IOS devices.

- Detects Cisco IOS using patterns like `version \d+\.\d+`, `boot system flash`, etc.
- Extracts interfaces, ACLs, VRFs, and routing information
- Handles common Cisco IOS syntax patterns

#### CiscoASAParser

The Cisco ASA parser handles configurations for Cisco ASA firewalls.

- Detects ASA configurations using patterns like `ASA Version` and `access-list.*extended`
- Extracts network objects, NAT rules, and security policies
- Specialized for firewall-specific configurations

#### CiscoNexusParser

The Cisco Nexus parser handles configurations for Cisco Nexus data center switches.

- Detects Nexus using patterns like `feature\s+` and `vpc domain`
- Extracts VLANs, VPC configurations, and VDCs
- Handles data center-specific features

### Fortinet Parsers

#### FortiGateParser

The FortiGate parser handles configurations for FortiGate firewalls.

- Detects FortiGate using patterns like `config\s+system\s+global`, `config\s+firewall\s+policy`
- Extracts interfaces, policies, address objects, service objects, and VPN configurations
- Handles FortiOS-specific syntax and objects

#### FortiSwitchParser

The FortiSwitch parser handles configurations for FortiSwitch devices.

- Detects FortiSwitch using patterns like `config\s+switch\s+vlan`, `config\s+switch\s+physical-port`
- Extracts VLANs and switch port configurations
- Handles switch-specific settings

### Juniper Parsers

#### JuniperJunOSParser

The Juniper JunOS parser handles configurations for Juniper network devices.

- Detects JunOS using patterns like `system\s+{\s+host-name\s+`, `interfaces\s+{\s+`
- Extracts interfaces, routing instances, security policies, and routing information
- Handles JunOS's unique hierarchical configuration format

## Parser Factory

The parser factory (`apps/parsers/parsers/factory.py`) provides a way to:

1. Automatically detect the appropriate parser for a configuration
2. Get a specific parser by device type slug

### Automatic Detection

```python
from apps.parsers.parsers.factory import ParserFactory

# Get the correct parser based on config content
config_text = "..."  # Device configuration
parser = ParserFactory.get_parser(config_text)
if parser:
    parsed_data = parser.parse(config_text)
else:
    # No compatible parser found
    pass
```

### Device Type Selection

```python
from apps.parsers.parsers.factory import ParserFactory

# Get parser by device type
parser = ParserFactory.get_parser_for_device_type("cisco-ios")
if parser:
    parsed_data = parser.parse(config_text)
else:
    # No parser available for this device type
    pass
```

## Integration with DeviceFile Model

The parsers are integrated with the `DeviceFile` model (`apps/parsers/models.py`), which represents an uploaded device configuration file. The model includes a `parse_file()` method that:

1. Gets the appropriate parser for the device type
2. Reads the configuration file
3. Parses the configuration
4. Updates the model's parsed status and any errors
5. (In a complete implementation) Saves the parsed data to the inventory

Example usage:

```python
device_file = DeviceFile.objects.get(pk=1)
if device_file.parse_file():
    # Successfully parsed
    print(f"Parsed {device_file.name}")
else:
    # Parsing failed
    print(f"Error parsing {device_file.name}: {device_file.parse_errors}")
```

## Adding a New Parser

To add support for a new device type:

1. Create a new class that inherits from `Parser`
2. Implement the required methods (`parse` and `detect_device_type`)
3. Override any optional methods as needed
4. Update the `ParserFactory._get_parser_classes()` and `get_parser_for_device_type()` methods
5. Add unit tests for the new parser

Example skeleton for a new parser:

```python
from apps.parsers.parsers.base import Parser
from typing import Dict, Any, List
import re

class NewDeviceParser(Parser):
    """Parser for New Device configurations."""
    
    def parse(self, config_text: str) -> Dict[str, Any]:
        """Parse New Device configuration."""
        if not self.detect_device_type(config_text):
            raise ValueError("Not a valid New Device configuration.")
        
        hostname = self.extract_hostname(config_text)
        
        return {
            "device_type": "new-device",
            "hostname": hostname,
            "interfaces": self.extract_interfaces(config_text),
            # Add other data as needed
        }
    
    def detect_device_type(self, config_text: str) -> bool:
        """Check if the configuration is from a New Device."""
        indicators = [
            # Add regex patterns that identify this device type
            r'device\s+version\s+\d+\.\d+',
            r'specific\s+syntax\s+pattern'
        ]
        
        for indicator in indicators:
            if re.search(indicator, config_text, re.IGNORECASE):
                return True
        
        return False
    
    def extract_hostname(self, config_text: str) -> str:
        """Extract hostname from New Device configuration."""
        # Implement hostname extraction logic
        pass
    
    # Implement other extraction methods as needed
```

## Testing

The parser system includes comprehensive tests:

1. Unit tests for the base Parser interface
2. Tests for each parser implementation
3. Tests for the ParserFactory
4. Integration tests with the DeviceFile model

To run the tests:

```bash
# Run all parser tests
python src/manage.py test apps.parsers.tests.test_parsers

# Run specific test case
python src/manage.py test apps.parsers.tests.test_parsers.TestCiscoIOSParser
```

Alternatively, you can use the direct test scripts:

```bash
# Test basic parser functionality
python src/test_parsers_directly.py

# Test parser factory
python src/test_parser_factory_directly.py

# Test DeviceFile integration
python src/test_device_file_parse.py
```

## Troubleshooting

Common issues:

1. **Invalid configuration format**: Ensure the configuration text is in the expected format for the device type.
2. **Parser not detecting device type**: Check if the configuration has the expected identifying patterns.
3. **Missing data in parsed output**: The parser might not support extracting that specific information, or the data might be in an unexpected format in the configuration.

If a parser fails to detect a valid configuration, you can examine the `detect_device_type` method of each parser to understand the patterns it's looking for.

## Future Enhancements

Planned improvements:

1. Support for additional device types (Arista, HPE, etc.)
2. Enhanced extraction capabilities for existing parsers
3. Performance optimizations for parsing large configurations
4. Version-specific parsing for different firmware versions 