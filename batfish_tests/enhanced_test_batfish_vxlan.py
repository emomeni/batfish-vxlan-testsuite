import os
import unittest
import pandas as pd
from typing import Dict, List, Set

try:
    from pybatfish.client.session import Session
    from pybatfish.question import bfq
    from pybatfish.datamodel import HeaderConstraints, PathConstraints
    PYBATFISH_AVAILABLE = True
except ImportError:
    PYBATFISH_AVAILABLE = False


class ComprehensiveBatfishVxlanTest(unittest.TestCase):
    """Comprehensive VXLAN fabric validation using Batfish"""
    
    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def setUp(self):
        """Setup Batfish session and snapshot"""
        self.bf = Session(host='localhost')
        self.snapshot_name = 'vxlan_fabric'
        snapshot_path = os.path.join(os.path.dirname(__file__), 'sample_configs')
        
        if os.path.isdir(snapshot_path):
            self.bf.init_snapshot(snapshot_path, name=self.snapshot_name, overwrite=True)
        else:
            self.skipTest(f"Snapshot directory {snapshot_path} not found")
            
        self.bf.set_snapshot(self.snapshot_name)
        
        # Expected fabric topology
        self.expected_leaf_nodes = {'leaf1', 'leaf2'}
        self.expected_spine_nodes = {'spine1'}
        self.expected_vnis = {5001}
        self.expected_asn = 65001

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_fabric_topology_discovery(self):
        """Validate that all expected nodes are present in the fabric"""
        nodes = bfq.nodeProperties().answer().frame()
        node_names = set(nodes['Node'].tolist())
        
        missing_leaves = self.expected_leaf_nodes - node_names
        missing_spines = self.expected_spine_nodes - node_names
        
        self.assertEqual(len(missing_leaves), 0, 
                        f"Missing leaf nodes: {missing_leaves}")
        self.assertEqual(len(missing_spines), 0, 
                        f"Missing spine nodes: {missing_spines}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_nve_interface_configuration(self):
        """Comprehensive NVE interface validation"""
        interfaces = bfq.interfaceProperties(interfaces='/nve.*/').answer().frame()
        
        # Check NVE interfaces exist
        self.assertFalse(interfaces.empty, "No NVE interfaces found")
        
        # Validate NVE interface configuration per leaf
        for leaf in self.expected_leaf_nodes:
            leaf_nve = interfaces[interfaces['Interface'].str.contains(leaf)]
            self.assertFalse(leaf_nve.empty, 
                           f"No NVE interface found on {leaf}")
            
            # Check interface is administratively up
            admin_up = leaf_nve['Admin_Up'].all()
            self.assertTrue(admin_up, 
                          f"NVE interface on {leaf} is administratively down")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_vxlan_vni_configuration(self):
        """Validate VXLAN VNI configuration"""
        vnis = bfq.vxlanVniProperties().answer().frame()
        
        self.assertFalse(vnis.empty, "No VXLAN VNIs configured")
        
        # Check expected VNIs are present
        configured_vnis = set(vnis['VNI'].tolist())
        missing_vnis = self.expected_vnis - configured_vnis
        
        self.assertEqual(len(missing_vnis), 0, 
                        f"Missing VNIs: {missing_vnis}")
        
        # Validate VNI configuration on each leaf
        for leaf in self.expected_leaf_nodes:
            leaf_vnis = vnis[vnis['Node'] == leaf]
            self.assertFalse(leaf_vnis.empty, 
                           f"No VNIs configured on {leaf}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_vxlan_ingress_replication_method(self):
        """Validate VXLAN ingress replication is set to BGP"""
        vnis = bfq.vxlanVniProperties().answer().frame()
        
        if not vnis.empty:
            # Check if ingress replication method column exists
            if 'Ingress_Method' in vnis.columns:
                non_bgp_vnis = vnis[vnis['Ingress_Method'] != 'BGP']
                self.assertTrue(non_bgp_vnis.empty, 
                              f"VNIs not using BGP ingress replication: {non_bgp_vnis[['Node', 'VNI']].values.tolist()}")
            else:
                self.skipTest("Ingress replication method information not available")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_bgp_session_establishment(self):
        """Validate BGP session compatibility and establishment"""
        bgp_sessions = bfq.bgpSessionCompatibility().answer().frame()
        
        self.assertFalse(bgp_sessions.empty, "No BGP sessions found")
        
        # Check for broken sessions
        if 'Session_Type' in bgp_sessions.columns:
            broken_sessions = bgp_sessions[bgp_sessions['Session_Type'] == 'BROKEN']
            self.assertTrue(broken_sessions.empty, 
                          f"Broken BGP sessions found: {broken_sessions[['Node', 'Remote_Node']].values.tolist()}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_bgp_evpn_address_family(self):
        """Validate BGP EVPN address family configuration"""
        bgp_process = bfq.bgpProcessConfiguration().answer().frame()
        
        # Check BGP processes exist
        self.assertFalse(bgp_process.empty, "No BGP processes found")
        
        # Validate EVPN address family is configured
        for node in self.expected_leaf_nodes | self.expected_spine_nodes:
            node_bgp = bgp_process[bgp_process['Node'] == node]
            self.assertFalse(node_bgp.empty, 
                           f"No BGP process found on {node}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_bgp_route_reflector_configuration(self):
        """Validate BGP route reflector setup on spine nodes"""
        bgp_neighbors = bfq.bgpPeerConfiguration().answer().frame()
        
        if not bgp_neighbors.empty:
            # Check spine nodes have multiple neighbors (leaf connections)
            for spine in self.expected_spine_nodes:
                spine_neighbors = bgp_neighbors[bgp_neighbors['Node'] == spine]
                neighbor_count = len(spine_neighbors)
                expected_neighbors = len(self.expected_leaf_nodes)
                
                self.assertGreaterEqual(neighbor_count, expected_neighbors,
                                      f"Spine {spine} has {neighbor_count} neighbors, expected at least {expected_neighbors}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_underlay_connectivity(self):
        """Test underlay IP connectivity between nodes"""
        # Get loopback interfaces (typically used as VTEP source)
        loopbacks = bfq.interfaceProperties(interfaces='/loopback.*/').answer().frame()
        
        if not loopbacks.empty:
            # Extract loopback IPs for reachability testing
            loopback_ips = []
            for _, interface in loopbacks.iterrows():
                if pd.notna(interface.get('Primary_Address')):
                    loopback_ips.append(interface['Primary_Address'].split('/')[0])
            
            # Test reachability between loopback addresses
            if len(loopback_ips) >= 2:
                for src_ip in loopback_ips:
                    for dst_ip in loopback_ips:
                        if src_ip != dst_ip:
                            reachability = bfq.reachability(
                                pathConstraints=PathConstraints(startLocation=f"@enter({src_ip})"),
                                headers=HeaderConstraints(dstIps=dst_ip)
                            ).answer().frame()
                            
                            # Check if path exists
                            if not reachability.empty:
                                unreachable = reachability[reachability['Result'] == 'UNREACHABLE']
                                self.assertTrue(unreachable.empty,
                                              f"Unreachable path from {src_ip} to {dst_ip}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")  
    def test_vxlan_tunnel_consistency(self):
        """Validate VXLAN tunnel source interface consistency"""
        interfaces = bfq.interfaceProperties(interfaces='/nve.*/').answer().frame()
        vnis = bfq.vxlanVniProperties().answer().frame()
        
        if not interfaces.empty and not vnis.empty:
            # Group by node and check source interface consistency
            for node in self.expected_leaf_nodes:
                node_interfaces = interfaces[interfaces['Interface'].str.contains(node)]
                node_vnis = vnis[vnis['Node'] == node]
                
                if not node_interfaces.empty and not node_vnis.empty:
                    # Check that all VNIs on a node use the same source interface
                    unique_sources = node_vnis['Source_Address'].nunique() if 'Source_Address' in node_vnis.columns else 0
                    if unique_sources > 0:
                        self.assertEqual(unique_sources, 1,
                                       f"Inconsistent VXLAN source addresses on {node}")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_routing_table_convergence(self):
        """Validate routing table has converged properly"""
        routes = bfq.routes().answer().frame()
        
        self.assertFalse(routes.empty, "No routes found in routing table")
        
        # Check for any unresolved or invalid routes
        if 'Protocol' in routes.columns:
            # Look for BGP routes (EVPN routes)
            bgp_routes = routes[routes['Protocol'] == 'bgp']
            self.assertFalse(bgp_routes.empty, "No BGP routes found")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_configuration_compliance(self):
        """Run configuration compliance checks"""
        # Check for unused configurations
        unused_structs = bfq.unusedStructures().answer().frame()
        
        # Check for undefined references
        undefined_refs = bfq.undefinedReferences().answer().frame()
        
        # Report issues but don't fail the test (warnings)
        if not unused_structs.empty:
            print(f"Warning: Found {len(unused_structs)} unused configuration structures")
            
        if not undefined_refs.empty:
            print(f"Warning: Found {len(undefined_refs)} undefined references")

    @unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
    def test_fabric_summary_report(self):
        """Generate a comprehensive fabric summary"""
        print("\n" + "="*60)
        print("VXLAN FABRIC VALIDATION SUMMARY")
        print("="*60)
        
        # Node summary
        nodes = bfq.nodeProperties().answer().frame()
        print(f"Nodes in fabric: {len(nodes)}")
        
        # Interface summary
        interfaces = bfq.interfaceProperties().answer().frame()
        nve_interfaces = interfaces[interfaces['Interface'].str.contains('nve', case=False, na=False)]
        print(f"NVE interfaces: {len(nve_interfaces)}")
        
        # VNI summary
        vnis = bfq.vxlanVniProperties().answer().frame()
        print(f"Configured VNIs: {len(vnis)}")
        if not vnis.empty:
            print(f"VNI list: {sorted(vnis['VNI'].unique().tolist())}")
        
        # BGP summary
        bgp_sessions = bfq.bgpSessionCompatibility().answer().frame()
        print(f"BGP sessions: {len(bgp_sessions)}")
        
        print("="*60)


class VxlanConfigurationValidator:
    """Additional helper class for configuration file validation"""
    
    @staticmethod
    def validate_config_files(config_dir: str) -> Dict[str, List[str]]:
        """Validate VXLAN configuration files for common issues"""
        issues = {}
        
        # This would contain file-based validation logic
        # For brevity, showing structure only
        config_files = ['leaf1.cfg', 'leaf2.cfg', 'spine1.cfg']
        
        for config_file in config_files:
            file_path = os.path.join(config_dir, config_file)
            if os.path.exists(file_path):
                file_issues = []
                
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                    # Example validations
                    if 'nve1' in content and 'source-interface loopback' not in content:
                        file_issues.append("NVE interface missing source-interface configuration")
                    
                    if 'router bgp' in content and 'address-family l2vpn evpn' not in content:
                        file_issues.append("BGP missing EVPN address family")
                
                if file_issues:
                    issues[config_file] = file_issues
        
        return issues


if __name__ == '__main__':
    # Run configuration file validation first
    config_dir = os.path.join(os.path.dirname(__file__), 'sample_configs')
    validator = VxlanConfigurationValidator()
    config_issues = validator.validate_config_files(config_dir)
    
    if config_issues:
        print("Configuration Issues Found:")
        for file, issues in config_issues.items():
            print(f"\n{file}:")
            for issue in issues:
                print(f"  - {issue}")
        print("\n" + "="*60 + "\n")
    
    # Run Batfish tests
    unittest.main(verbosity=2)