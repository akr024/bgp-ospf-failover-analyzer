import unittest

from diff import diff_snapshots

def make_snapshot(
    ospf_state="Full",
    bgp_state="Established",
    next_hop="10.0.13.1",
):
    return {
        "routers": {
            "spine1": {
                "ospf": {
                    "neighbors": {
                        "10.255.0.1": [
                            {
                                "converged": ospf_state,
                                "ifaceAddress": "10.0.13.1",
                                "ifaceName": "eth1:10.0.13.1",
                            }
                        ]
                    }
                },
                "bgp": {
                    "peers": {
                        "10.0.35.2": {
                            "state": bgp_state,
                            "remoteAs": 65100,
                        }
                    }
                },
                "routes": {
                    "10.255.0.1/32": [
                        {
                            "protocol": "ospf",
                            "selected": True,
                            "installed": True,
                            "nexthops": [
                                {
                                    "ip": next_hop,
                                    "active": True,
                                }
                            ],
                        }
                    ]
                },
                "error": None,
            }
        }
    }


class TestDiff(unittest.TestCase):

    def test_identical_snapshots(self):
        snapshot = make_snapshot()

        events = diff_snapshots(
            snapshot,
            snapshot,
        )

        self.assertEqual(events, [])

    def test_ospf_state_change(self):
        old = make_snapshot(
            ospf_state="Full"
        )

        new = make_snapshot(
            ospf_state="Down"
        )

        events = diff_snapshots(
            old,
            new,
        )

        event_names = {
            event["event"]
            for event in events
        }

        self.assertIn(
            "neighbor_state_changed",
            event_names,
        )

    def test_bgp_state_change(self):
        old = make_snapshot(
            bgp_state="Established"
        )

        new = make_snapshot(
            bgp_state="Active"
        )

        events = diff_snapshots(
            old,
            new,
        )

        event_names = {
            event["event"]
            for event in events
        }

        self.assertIn(
            "peer_state_changed",
            event_names,
        )

    def test_next_hop_change(self):
        old = make_snapshot(
            next_hop="10.0.13.1"
        )

        new = make_snapshot(
            next_hop="10.0.14.1"
        )

        events = diff_snapshots(
            old,
            new,
        )

        event_names = {
            event["event"]
            for event in events
        }

        self.assertIn(
            "next_hop_changed",
            event_names,
        )

    def test_ecmp_order_does_not_change(self):
        old = {
            "routers": {
                "leaf1": {
                    "routes": {
                        "0.0.0.0/0": {
                            "protocols": ["ospf"],
                            "next_hops": [
                                "10.0.13.2",
                                "10.0.14.2",
                            ],
                        }
                    }
                }
            }
        }

        new = {
            "routers": {
                "leaf1": {
                    "routes": {
                        "0.0.0.0/0": {
                            "protocols": ["ospf"],
                            "next_hops": [
                                "10.0.14.2",
                                "10.0.13.2",
                            ],
                        }
                    }
                }
            }
        }

        self.assertEqual(
            sorted(
                old["routers"]["leaf1"]["routes"]
                ["0.0.0.0/0"]["next_hops"]
            ),
            sorted(
                new["routers"]["leaf1"]["routes"]
                ["0.0.0.0/0"]["next_hops"]
            ),
        )


if __name__ == "__main__":
    unittest.main()
