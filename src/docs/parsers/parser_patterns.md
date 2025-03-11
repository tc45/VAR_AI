# Parser Detection Patterns

This document provides a quick reference for the patterns used by each parser to detect device types.

## Cisco Patterns

### CiscoIOSParser

```python
# Patterns that indicate Cisco IOS
ios_indicators = [
    r'version \d+\.\d+',
    r'boot system flash',
    r'service\s+',
    r'ip classless',
    r'interface [A-Za-z]+\d+\/\d+'
]
```

### CiscoASAParser

```python
# Patterns that indicate Cisco ASA
asa_indicators = [
    r'ASA Version',
    r'access-list.*extended',
    r'fixup protocol',
    r'security-level',
    r'nameif'
]
```

### CiscoNexusParser

```python
# Patterns that indicate Cisco Nexus
nexus_indicators = [
    r'feature\s+',
    r'vpc domain',
    r'Nexus\s+\d+',
    r'fabricpath',
    r'vdc\s+'
]
```

## Fortinet Patterns

### FortiGateParser

```python
# Patterns that indicate FortiGate
fortigate_indicators = [
    r'config\s+system\s+global',
    r'config\s+firewall\s+policy',
    r'config\s+vpn\s+ipsec\s+phase1-interface',
    r'set\s+vdom\s+',
    r'config\s+firewall\s+address'
]
```

### FortiSwitchParser

```python
# Patterns that indicate FortiSwitch
fortiswitch_indicators = [
    r'config\s+switch\s+vlan',
    r'config\s+switch\s+physical-port',
    r'config-version=[A-Z\d]+-FGT_',
    r'FortiSwitch\s+\d+',
    r'FortiOS'
]
```

## Juniper Patterns

### JuniperJunOSParser

```python
# Patterns that indicate Juniper JunOS
junos_indicators = [
    r'system\s+{\s+host-name\s+',
    r'interfaces\s+{\s+',
    r'protocols\s+{\s+',
    r'routing-options\s+{\s+',
    r'policy-options\s+{\s+',
    r'security\s+{\s+',
    r'version\s+\d+\.\d+[A-Z]\d+'
]
```

## Adding New Device Type Patterns

When implementing a new device parser, look for patterns that are:

1. **Unique** to the device type (unlikely to appear in other vendor configurations)
2. **Common** in most configurations for that device type
3. **Stable** across different versions or models

Good candidates for detection patterns include:

- Version or firmware identifiers
- Device-specific commands or syntax
- Configuration structure markers
- Vendor-specific feature names

Example for adding patterns for a new device:

```python
# Patterns that would identify a Palo Alto firewall
paloalto_indicators = [
    r'set deviceconfig system',
    r'set vsys',
    r'set rulebase security rules',
    r'set network interface ethernet',
    r'set zone'
]
``` 