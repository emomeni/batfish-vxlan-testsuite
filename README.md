# Batfish VXLAN Network Testing

This project provides automated testing for VXLAN network configurations using Batfish, a network configuration analysis tool. It validates VXLAN and BGP EVPN configurations across network devices.

## Overview

The test suite analyzes network device configurations to verify:
- NVE (Network Virtualization Edge) interface presence and configuration
- BGP session establishment for EVPN (Ethernet VPN) functionality
- VXLAN overlay network connectivity

## Prerequisites

### Required Software
- Python 3.7 or higher
- pip (Python package installer)

### Required Python Packages
```bash
pip install pybatfish unittest
```

### Batfish Service
You need a running Batfish service instance. You can either:

#### Option 1: Docker (Recommended)
```bash
docker run -d -p 9997:9997 -p 9996:9996 batfishorg/batfish
```

#### Option 2: Local Installation
Follow the [Batfish installation guide](https://github.com/batfish/batfish) for local setup.

## Project Structure

```
project-root/
├── test_batfish_vxlan.py    # Main test script
├── sample_configs/          # Network configuration directory
│   ├── leaf1.cfg           # Leaf switch configuration
│   └── spine1.cfg          # Spine switch configuration
└── README.md               # This file
```

## Configuration Files

### leaf1.cfg
Contains the leaf switch configuration with:
- NVE interface configuration
- VXLAN VNI mapping
- BGP EVPN neighbor relationships

### spine1.cfg
Contains the spine switch configuration with:
- BGP EVPN route reflector setup
- Neighbor relationships with leaf switches

## Running the Tests

### Basic Test Execution
```bash
python test_batfish_vxlan.py
```

### Verbose Output
```bash
python test_batfish_vxlan.py -v
```

### Running Specific Tests
```bash
python -m unittest test_batfish_vxlan.BatfishVxlanTest.test_nve_interface_exists
python -m unittest test_batfish_vxlan.BatfishVxlanTest.test_bgp_peers_established
```

## Test Cases

### 1. NVE Interface Validation (`test_nve_interface_exists`)
- **Purpose**: Verifies that Network Virtualization Edge interfaces are configured
- **Validation**: Checks for interfaces matching pattern `/nve.*/`
- **Expected Result**: At least one NVE interface should be present

### 2. BGP Session Compatibility (`test_bgp_peers_established`)
- **Purpose**: Validates BGP EVPN session configuration
- **Validation**: Analyzes BGP neighbor compatibility
- **Expected Result**: BGP peers should be properly configured for EVPN

## Configuration Requirements

For tests to pass, ensure your network configurations include:

### VXLAN Configuration
- NVE interfaces with proper source interface
- VNI (VXLAN Network Identifier) mappings
- Ingress replication protocol settings

### BGP EVPN Configuration
- BGP router process with appropriate AS numbers
- EVPN address family configuration
- Extended community advertisement
- Proper neighbor relationships

## Troubleshooting

### Common Issues

#### 1. Batfish Service Not Running
```
Error: Connection refused to localhost:9997
```
**Solution**: Ensure Batfish service is running on localhost:9997

#### 2. Missing pybatfish Package
```
ImportError: No module named 'pybatfish'
```
**Solution**: Install pybatfish using `pip install pybatfish`

#### 3. No Configuration Files Found
```
Error: snapshot_path directory not found
```
**Solution**: Ensure `sample_configs/` directory exists with configuration files

#### 4. Empty Test Results
```
AssertionError: No NVE interfaces found in snapshot
```
**Solution**: Verify NVE interfaces are properly configured in your device configs

### Debug Mode
To enable detailed logging, modify the test script:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Extending the Tests

### Adding New Test Cases
```python
@unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
def test_vxlan_vni_consistency(self):
    """Verify VNI consistency across devices"""
    # Your test logic here
    pass
```

### Adding New Configuration Files
1. Place new `.cfg` files in the `sample_configs/` directory
2. Batfish will automatically include them in the snapshot analysis

## Sample Network Topology

```
    [Spine1 - 2.2.2.2/32]
           |
    [Leaf1 - 1.1.1.1/32]
        |
    [NVE1 - VNI 5001]
```

## Expected Output

Successful test run:
```
test_bgp_peers_established (__main__.BatfishVxlanTest) ... ok
test_nve_interface_exists (__main__.BatfishVxlanTest) ... ok

----------------------------------------------------------------------
Ran 2 tests in 5.231s

OK
```

## Additional Resources

- [Batfish Documentation](https://batfish.readthedocs.io/)
- [pybatfish GitHub Repository](https://github.com/batfish/pybatfish)
- [Cisco Nexus 9000 VXLAN BGP EVPN Design Guide](https://www.cisco.com/c/en/us/td/docs/dcn/whitepapers/cisco-vxlan-bgp-evpn-design-and-implementation-guide.html)
- [Cisco Nexus 9000 VXLAN Configuration Guide](https://www.cisco.com/c/en/us/td/docs/dcn/nx-os/nexus9000/103x/configuration/vxlan/cisco-nexus-9000-series-nx-os-vxlan-configuration-guide-release-103x.html)
- [VXLAN EVPN Multi-Site White Paper](https://www.cisco.com/c/en/us/products/collateral/switches/nexus-9000-series-switches/white-paper-c11-739942.html)
- [BGP EVPN RFC 7432](https://tools.ietf.org/html/rfc7432)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add your tests and configurations
4. Submit a pull request

## License

This project is provided as-is for educational and testing purposes.

## Support

For issues related to:
- **Batfish**: Check the [Batfish GitHub Issues](https://github.com/batfish/batfish/issues)
- **This Project**: Review the troubleshooting section above

---

*Last updated: July 2025*