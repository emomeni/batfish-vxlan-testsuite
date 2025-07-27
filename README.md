# Batfish VXLAN Testing Framework

A comprehensive network validation framework for VXLAN BGP EVPN fabrics using Batfish network analysis platform.

## Overview

This framework provides automated testing and validation capabilities for VXLAN BGP EVPN network fabrics. It uses Batfish to analyze network configurations and validate proper deployment of:

- VXLAN Network Virtualization Edge (NVE) interfaces
- BGP EVPN control plane configuration
- VXLAN Network Identifiers (VNIs)
- Underlay connectivity and routing
- BGP route reflector setup
- Configuration compliance

## Features

### Core Validation Tests
- **Fabric Topology Discovery**: Validates all expected leaf and spine nodes are present
- **NVE Interface Configuration**: Comprehensive NVE interface validation
- **VXLAN VNI Configuration**: Validates VNI configuration across fabric
- **BGP Session Establishment**: Checks BGP session compatibility
- **BGP EVPN Address Family**: Validates EVPN address family configuration
- **Route Reflector Configuration**: Validates spine nodes as BGP route reflectors
- **Underlay Connectivity**: Tests IP reachability between VTEP endpoints
- **VXLAN Tunnel Consistency**: Validates source interface consistency
- **Routing Table Convergence**: Ensures proper route convergence
- **Configuration Compliance**: Identifies unused structures and undefined references

### Additional Features
- Configuration file validation (pre-Batfish analysis)
- Comprehensive fabric summary reporting
- Graceful handling of missing dependencies
- Detailed error reporting and diagnostics

## Requirements

### Software Dependencies
- Python 3.7+
- pybatfish
- pandas
- Batfish server (Docker recommended)

### Hardware/Infrastructure
- Docker runtime (for Batfish server)
- Network configuration files in supported formats

## Installation

### 1. Install Python Dependencies
Install the required packages using the provided `requirements.txt` file:
```bash
pip install -r requirements.txt
```

### 2. Start Batfish Server
Using Docker (recommended):
```bash
docker run -d --name batfish -p 9997:9997 -p 9996:9996 batfish/batfish
```

Or download and run Batfish server manually from [Batfish GitHub](https://github.com/batfish/batfish).

### 3. Clone/Download Framework Files
Ensure you have the following files in your project directory:
```
project/
├── enhanced_test_batfish_vxlan.py
├── test_batfish_vxlan.py
├── sample_configs/
│   ├── leaf1.cfg
│   ├── leaf2.cfg
│   └── spine1.cfg
└── README.md
```

## Configuration Files

The framework includes sample VXLAN BGP EVPN configurations:

### Fabric Topology
- **leaf1**: VTEP with loopback 1.1.1.1, VNI 5001
- **leaf2**: VTEP with loopback 1.1.1.2, VNI 5001  
- **spine1**: BGP route reflector with loopback 2.2.2.2

### Key Configuration Elements
- **VNI 5001**: Mapped to VLAN 10 across leaf switches
- **BGP ASN 65001**: Used across entire fabric
- **Ingress Replication**: Configured to use BGP
- **Underlay Addressing**: Point-to-point links between spine-leaf

## Usage

### Basic Testing
Run the basic test suite:
```bash
python test_batfish_vxlan.py
```

### Comprehensive Testing
Run the enhanced test suite with detailed validation:
```bash
python enhanced_test_batfish_vxlan.py
```

### Running Specific Tests
```bash
python -m unittest enhanced_test_batfish_vxlan.ComprehensiveBatfishVxlanTest.test_fabric_topology_discovery
```

### Running Tests with Verbose Output
```bash
python enhanced_test_batfish_vxlan.py -v
```

## Test Scripts Comparison

This framework provides two test scripts with different levels of validation depth:

### `test_batfish_vxlan.py` - Basic Validation Suite

**Purpose**: Quick validation of core VXLAN functionality
**Tests**: 4 basic tests
**Runtime**: ~10-15 seconds

| Test Method | Description | Validation Level |
|-------------|-------------|------------------|
| `test_nve_interface_exists` | Verifies NVE interfaces are configured | Basic presence check |
| `test_bgp_peers_established` | Checks BGP session compatibility | Basic session validation |
| `test_vxlan_vni_defined` | Ensures VNI configuration exists | Basic VNI presence |
| `test_vxlan_ingress_replication_bgp` | Validates BGP ingress replication | Basic protocol check |

**Use Case**: 
- Quick smoke tests
- CI/CD pipeline integration
- Initial configuration validation
- Development environment testing

### `enhanced_test_batfish_vxlan.py` - Comprehensive Validation Suite

**Purpose**: Deep fabric validation with detailed analysis
**Tests**: 12 comprehensive tests
**Runtime**: ~45-60 seconds

| Test Method | Description | Validation Level |
|-------------|-------------|------------------|
| `test_fabric_topology_discovery` | Validates all expected nodes present | ✅ Node inventory verification |
| `test_nve_interface_configuration` | Comprehensive NVE interface validation | ✅ Admin status, per-leaf checks |
| `test_vxlan_vni_configuration` | Detailed VNI configuration analysis | ✅ VNI presence per leaf |
| `test_vxlan_ingress_replication_method` | Validates BGP ingress replication | ✅ Protocol method verification |
| `test_bgp_session_establishment` | BGP session compatibility analysis | ✅ Broken session detection |
| `test_bgp_evpn_address_family` | BGP EVPN address family validation | ✅ Process configuration check |
| `test_bgp_route_reflector_configuration` | Route reflector setup validation | ✅ Neighbor count verification |
| `test_underlay_connectivity` | IP reachability testing | ✅ Loopback-to-loopback paths |
| `test_vxlan_tunnel_consistency` | Source interface consistency | ✅ Per-node source validation |
| `test_routing_table_convergence` | Route convergence analysis | ✅ BGP route presence |
| `test_configuration_compliance` | Configuration quality checks | ✅ Unused/undefined detection |
| `test_fabric_summary_report` | Comprehensive fabric reporting | ✅ Detailed statistics output |

**Use Case**:
- Production readiness validation
- Detailed troubleshooting
- Change impact assessment
- Compliance verification

## Feature Comparison Matrix

| Feature | Basic Script | Enhanced Script |
|---------|--------------|-----------------|
| **Test Coverage** | 4 tests | 12 tests |
| **Execution Time** | Fast (~15s) | Comprehensive (~60s) |
| **Error Details** | Basic assertions | Detailed diagnostics |
| **Fabric Topology Validation** | ❌ | ✅ |
| **Per-Node Analysis** | ❌ | ✅ |
| **Underlay Testing** | ❌ | ✅ |
| **Route Reflector Validation** | ❌ | ✅ |
| **Configuration Compliance** | ❌ | ✅ |
| **Summary Reporting** | ❌ | ✅ |
| **Pre-Batfish Config Validation** | ❌ | ✅ |
| **Reachability Testing** | ❌ | ✅ |
| **Custom Validation Class** | ❌ | ✅ |

## When to Use Which Script

### Use Basic Script (`test_batfish_vxlan.py`) when:
- ⚡ Quick validation needed
- 🔄 Running in CI/CD pipelines
- 🧪 Development environment testing
- 🎯 Focused on core VXLAN functionality
- ⏱️ Time constraints exist

### Use Enhanced Script (`enhanced_test_batfish_vxlan.py`) when:
- 🏭 Production deployment validation
- 🔍 Detailed troubleshooting required
- 📊 Comprehensive reporting needed
- 🛡️ Security/compliance validation
- 🌐 Full fabric health assessment
- 📈 Change impact analysis

## Test Categories

### 1. Basic Validation (`test_batfish_vxlan.py`)
- NVE interface existence
- BGP peer establishment
- VXLAN VNI definition
- Ingress replication method validation

### 2. Comprehensive Validation (`enhanced_test_batfish_vxlan.py`)
- All basic validations plus:
- Detailed fabric topology checking
- BGP route reflector validation
- Underlay connectivity testing
- Configuration consistency checks
- Fabric summary reporting

## Configuration Customization

### Modifying Expected Values
Edit the `setUp()` method in `ComprehensiveBatfishVxlanTest`:

```python
# Expected fabric topology
self.expected_leaf_nodes = {'leaf1', 'leaf2', 'leaf3'}  # Add more leaves
self.expected_spine_nodes = {'spine1', 'spine2'}        # Add more spines
self.expected_vnis = {5001, 5002, 5003}                # Add more VNIs
self.expected_asn = 65001                               # Change ASN
```

### Adding Custom Configuration Files
1. Place configuration files in the `sample_configs/` directory
2. Update node names in test setup
3. Ensure configuration files follow supported vendor formats

## Supported Vendor Formats

Batfish supports configuration files from:
- Cisco (IOS, IOS-XR, NX-OS)
- Juniper (Junos)
- Arista (EOS)
- And many others

## Troubleshooting

### Common Issues

**1. Batfish Server Connection Failed**
```
Error: Could not connect to Batfish server
```
Solution: Ensure Batfish server is running on localhost:9997

**2. Snapshot Directory Not Found**
```
Error: Snapshot directory sample_configs not found
```
Solution: Ensure `sample_configs/` directory exists with configuration files

**3. No NVE Interfaces Found**
```
AssertionError: No NVE interfaces found in snapshot
```
Solution: Verify configuration files contain proper NVE interface configuration

**4. pybatfish Import Error**
```
ImportError: No module named 'pybatfish'
```
Solution: Install pybatfish using `pip install pybatfish`

### Debug Mode
Enable verbose logging in tests:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Expected Test Output

### Successful Run Example
```
test_bgp_evpn_address_family (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_bgp_route_reflector_configuration (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_bgp_session_establishment (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_configuration_compliance (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_fabric_summary_report (__main__.ComprehensiveBatfishVxlanTest) ... 
============================================================
VXLAN FABRIC VALIDATION SUMMARY
============================================================
Nodes in fabric: 3
NVE interfaces: 2
Configured VNIs: 2
VNI list: [5001]
BGP sessions: 4
============================================================
ok
test_fabric_topology_discovery (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_nve_interface_configuration (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_routing_table_convergence (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_underlay_connectivity (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_vxlan_ingress_replication_method (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_vxlan_tunnel_consistency (__main__.ComprehensiveBatfishVxlanTest) ... ok
test_vxlan_vni_configuration (__main__.ComprehensiveBatfishVxlanTest) ... ok

----------------------------------------------------------------------
Ran 12 tests in 45.123s

OK
```

## Extending the Framework

### Adding New Test Cases
```python
@unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
def test_custom_validation(self):
    """Add your custom validation logic"""
    # Your test implementation
    pass
```

### Adding Configuration Validators
Extend the `VxlanConfigurationValidator` class:
```python
@staticmethod
def validate_custom_config(config_content: str) -> List[str]:
    """Add custom configuration validation"""
    issues = []
    # Your validation logic
    return issues
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is provided as-is for educational and testing purposes. Please ensure compliance with your organization's testing and automation policies.

## Support

For issues related to:
- **Batfish**: Visit [Batfish GitHub](https://github.com/batfish/batfish)
- **This Framework**: Check configuration files and test setup
- **Network Configuration**: Consult vendor documentation

## Version History

- **v1.0**: Basic VXLAN validation tests
- **v2.0**: Comprehensive validation with underlay testing
- **v2.1**: Added configuration file validation and summary reporting

---

**Note**: This framework is designed for network validation and testing. Always test in non-production environments first.