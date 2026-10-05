ROUTE_PROTOCOLS = {"ospf", "bgp"}


def normalize_ospf(data: dict) -> dict:

    neighbors = {}

    for router_id, entries in data.get("neighbors", {}).items():
        normalized_entries = []

        for entry in entries:
            normalized_entries.append(
                {
                    "state": entry.get("converged", entry.get("nbrState")),
                    "address": entry.get("ifaceAddress"),
                    "interface": entry.get("ifaceName"),
                }
            )

        neighbors[router_id] = sorted(
            normalized_entries,
            key=lambda entry: (
                entry["address"] or "",
                entry["interface"] or "",
                entry["state"] or "",
            ),
        )

    return neighbors


def normalize_bgp(data: dict) -> dict:

    peers = {}

    for peer_ip, entry in data.get("peers", {}).items():
        peers[peer_ip] = {
            "state": entry.get("state"),
            "remote_as": entry.get("remoteAs"),
        }

    return peers


def normalize_routes(data: dict) -> dict:

    routes = {}

    for prefix, entries in data.items():
        relevant_entries = [
            entry
            for entry in entries
            if entry.get("protocol") in ROUTE_PROTOCOLS
            and entry.get("selected") is True
            and entry.get("installed") is True
        ]

        if not relevant_entries:
            continue

        protocols = set()
        next_hops = set()

        for entry in relevant_entries:
            protocols.add(entry["protocol"])

            for nexthop in entry.get("nexthops", []):
                if nexthop.get("ip") and nexthop.get("active",False):
                    next_hops.add(nexthop["ip"])

        routes[prefix] = {
            "protocols": sorted(protocols),
            "next_hops": sorted(next_hops),
        }

    return routes


def normalize_snapshot(snapshot: dict) -> dict:

    normalized = {"routers": {}}

    for router_name, router_state in snapshot.get("routers", {}).items():
        if router_state.get("error"):
            normalized["routers"][router_name] = {
                "error": router_state["error"]
            }
            continue

        normalized_router = {
            "routes": normalize_routes(router_state.get("routes") or {})
        }

        if router_state.get("ospf") is not None:
            normalized_router["ospf"] = normalize_ospf(
                router_state["ospf"]
            )

        if router_state.get("bgp") is not None:
            normalized_router["bgp"] = normalize_bgp(
                router_state["bgp"]
            )

        normalized["routers"][router_name] = normalized_router

    return normalized
