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
class BatfishVxlanTest(RequiresPybatfishTestCase):
    BF_HOST = 'localhost'
    SNAPSHOT_NAME = 'nxos_vxlan'

    def setUp(self):
        self.bf = Session(host=self.BF_HOST)
        snapshot_path = os.path.join(os.path.dirname(__file__), 'sample_configs')
        if not os.path.isdir(snapshot_path):
            self.skipTest(f"Snapshot directory {snapshot_path} not found")
        self.bf.init_snapshot(snapshot_path, name=self.SNAPSHOT_NAME, overwrite=True)
        self.bf.set_snapshot(self.SNAPSHOT_NAME)

    def test_nve_interface_exists(self):
        """Verify that at least one NVE interface is configured"""
        interfaces = bfq.interfaceProperties(interfaces='/nve.*/').answer().frame()
        self.assertFalse(interfaces.empty, "No NVE interfaces found in snapshot")

    def test_bgp_peers_established(self):
        """Check that BGP sessions are configured"""
        peers = bfq.bgpSessionCompatibility().answer().frame()
        self.assertFalse(peers.empty, "No BGP peers found in snapshot")

    def test_vxlan_vni_defined(self):
        """Ensure at least one VXLAN VNI is defined"""
        vnis = bfq.vxlanVniProperties().answer().frame()
        self.assertFalse(vnis.empty, "No VXLAN VNIs found in snapshot")

    def test_vxlan_ingress_replication_bgp(self):
        """Validate that VXLAN uses BGP for ingress replication"""
        vnis = bfq.vxlanVniProperties().answer().frame()
        if not vnis.empty and "Ingress_Method" in vnis.columns:
            self.assertTrue((vnis["Ingress_Method"] == "BGP").all(),
                            "Ingress replication not set to BGP for all VNIs")


if __name__ == '__main__':
    unittest.main()