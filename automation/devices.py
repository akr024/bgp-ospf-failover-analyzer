OSPF_COMMAND = 'vtysh -c "show ip ospf neighbor json"'
BGP_COMMAND = 'vtysh -c "show bgp ipv4 unicast summary json"'
ROUTE_COMMAND = 'vtysh -c "show ip route json"'

CONVERGENCE_SCENARIOS = {
    "spine1_bb1": {
        "monitor": "backbone1",
        "prefix": "10.255.0.1/32",
        "failed_next_hop": "10.0.35.1",
    },
    "spine2_bb2": {
        "monitor": "backbone2",
        "prefix": "10.255.0.1/32",
        "failed_next_hop": "10.0.46.1",
    },
}

FAILURE_SCENARIOS = {
    "spine1_bb1": {
        "router": "spine1",
        "interface": "eth3",
    },
    "spine1_bb2": {
        "router": "spine1",
        "interface": "eth4",
    },
    "spine2_bb2": {
        "router": "spine2",
        "interface": "eth3",
    },
    "spine2_bb1": {
        "router": "spine2",
        "interface": "eth4",
    },
}

ROUTERS = {
        "leaf1":{
            "ospf":True,
            "bgp":False,
            "host":"172.20.20.4"
            },
        "leaf2":{
            "ospf":True,
            "bgp":False,
            "host":"172.20.20.5"
            },
        "spine1":{
            "ospf":True,
            "bgp":True,
            "host":"172.20.20.2"
            },
        "spine2":{
            "ospf":True,
            "bgp":True,
            "host":"172.20.20.6"
            },
        "backbone1":{
            "ospf":False,
            "bgp":True,
            "host":"172.20.20.7"
            },
        "backbone2":{
            "ospf":False,
            "bgp":True,
            "host":"172.20.20.3"
            }
}
