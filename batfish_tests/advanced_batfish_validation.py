import os
import unittest

try:
    from pybatfish.client.session import Session
    from pybatfish.question import bfq
    PYBATFISH_AVAILABLE = True
except ImportError:  # pybatfish is not installed
    PYBATFISH_AVAILABLE = False


class RequiresPybatfishTestCase(unittest.TestCase):
    """Base test case that skips tests if pybatfish is unavailable."""

    @classmethod
    def setUpClass(cls):
        if not PYBATFISH_AVAILABLE:
            raise unittest.SkipTest("pybatfish not available")


@unittest.skipUnless(PYBATFISH_AVAILABLE, "pybatfish not available")
class AdvancedBatfishVxlanTest(RequiresPybatfishTestCase):
    """Additional VXLAN fabric validation tests using Batfish."""

    BF_HOST = 'localhost'
    SNAPSHOT_NAME = 'vxlan_fabric_advanced'

    def setUp(self):
        self.bf = Session(host=self.BF_HOST)
        snapshot_path = os.path.join(os.path.dirname(__file__), 'sample_configs')
        if not os.path.isdir(snapshot_path):
            self.skipTest(f"Snapshot directory {snapshot_path} not found")
        self.bf.init_snapshot(snapshot_path, name=self.SNAPSHOT_NAME, overwrite=True)
        self.bf.set_snapshot(self.SNAPSHOT_NAME)

        self.expected_leaf_nodes = {'leaf1', 'leaf2'}
        self.expected_spine_nodes = {'spine1'}
        self.expected_asn = 65001
        self.vlan_vni_map = {10: 5001}

    def test_unique_loopback_ips(self):
        """Verify loopback0 addresses are unique and /32."""
        interfaces = bfq.interfaceProperties(interfaces='/loopback0/').answer().frame()
        self.assertFalse(interfaces.empty, "No loopback0 interfaces found")
        ips = interfaces['Primary_Address'].dropna().str.split('/').str[0]
        self.assertEqual(len(ips), len(set(ips)), "Duplicate loopback IPs found")
        masks = interfaces['Primary_Address'].dropna().str.split('/').str[1]
        self.assertTrue((masks == '32').all(), "Loopback addresses must be /32")

    def test_bgp_asn_consistency(self):
        """Ensure all nodes run the expected BGP ASN."""
        bgp_process = bfq.bgpProcessConfiguration().answer().frame()
        self.assertFalse(bgp_process.empty, "No BGP process information found")
        asns = bgp_process['Local_AS'].unique()
        self.assertEqual(len(asns), 1, f"Multiple ASNs found: {asns}")
        self.assertEqual(asns[0], self.expected_asn, f"Unexpected ASN {asns[0]}")

    def test_evpn_mac_routes_advertised(self):
        """Check that EVPN MAC routes (Type 2) exist."""
        evpn_routes = bfq.evpnRoutes().answer().frame()
        if 'Route_Type' in evpn_routes.columns:
            mac_routes = evpn_routes[evpn_routes['Route_Type'] == 'TYPE_2']
        else:
            mac_routes = evpn_routes
        self.assertFalse(mac_routes.empty, "No EVPN MAC routes found")

    def test_evpn_prefix_routes_advertised(self):
        """Check that EVPN prefix routes (Type 5) exist."""
        evpn_routes = bfq.evpnRoutes().answer().frame()
        if 'Route_Type' in evpn_routes.columns:
            prefix_routes = evpn_routes[evpn_routes['Route_Type'] == 'TYPE_5']
        else:
            prefix_routes = evpn_routes
        self.assertFalse(prefix_routes.empty, "No EVPN prefix routes found")

    def test_vlan_vni_mapping_consistency(self):
        """Verify VLAN to VNI mappings are consistent on all leaves."""
        vnis = bfq.vxlanVniProperties().answer().frame()
        self.assertFalse(vnis.empty, "No VNI information found")
        for vlan, vni in self.vlan_vni_map.items():
            if 'Vlan' in vnis.columns:
                mapping = vnis[(vnis['VNI'] == vni) & (vnis['Vlan'] == vlan)]
            else:
                mapping = vnis[vnis['VNI'] == vni]
            self.assertFalse(mapping.empty, f"VLAN {vlan} not mapped to VNI {vni}")


if __name__ == '__main__':
    unittest.main(verbosity=2)
