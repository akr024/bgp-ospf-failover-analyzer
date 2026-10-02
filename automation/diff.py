import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from state import normalize_snapshot

def diff_ospf_neighbors(
    router: str,
    old: dict,
    new: dict
) -> list[dict]:

    events = []

    for neighbor in sorted(set(old) | set(new)):

        if neighbor not in old:
            events.append(
                {
                    "router": router,
                    "protocol": "ospf",
                    "event": "neighbor_added",
                    "peer": neighbor,
                    "new": new[neighbor],
                }
            )

        elif neighbor not in new:
            events.append(
                {
                    "router": router,
                    "protocol": "ospf",
                    "event": "neighbor_removed",
                    "peer": neighbor,
                    "old": old[neighbor],
                }
            )

        else:
            old_states = sorted(
                entry.get("state")
                for entry in old[neighbor]
            )

            new_states = sorted(
                entry.get("state")
                for entry in new[neighbor]
            )

            if old_states != new_states:
                events.append(
                    {
                        "router": router,
                        "protocol": "ospf",
                        "event": "neighbor_state_changed",
                        "peer": neighbor,
                        "old": old_states,
                        "new": new_states,
                    }
                )

    return events


def diff_bgp_peers(
    router: str,
    old: dict,
    new: dict
) -> list[dict]:

    events = []

    for peer in sorted(set(old) | set(new)):

        if peer not in old:
            events.append(
                {
                    "router": router,
                    "protocol": "bgp",
                    "event": "peer_added",
                    "peer": peer,
                    "new": new[peer],
                }
            )

        elif peer not in new:
            events.append(
                {
                    "router": router,
                    "protocol": "bgp",
                    "event": "peer_removed",
                    "peer": peer,
                    "old": old[peer],
                }
            )

        elif old[peer]["state"] != new[peer]["state"]:
            events.append(
                {
                    "router": router,
                    "protocol": "bgp",
                    "event": "peer_state_changed",
                    "peer": peer,
                    "old": old[peer]["state"],
                    "new": new[peer]["state"],
                }
            )

    return events


def diff_routes(
    router: str,
    old: dict,
    new: dict
) -> list[dict]:

    events = []

    for prefix in sorted(set(old) | set(new)):

        if prefix not in old:
            events.append(
                {
                    "router": router,
                    "protocol": "route",
                    "event": "route_added",
                    "prefix": prefix,
                    "new": new[prefix],
                }
            )

        elif prefix not in new:
            events.append(
                {
                    "router": router,
                    "protocol": "route",
                    "event": "route_removed",
                    "prefix": prefix,
                    "old": old[prefix],
                }
            )

        else:

            if (
                old[prefix]["next_hops"]
                != new[prefix]["next_hops"]
            ):
                events.append(
                    {
                        "router": router,
                        "protocol": "route",
                        "event": "next_hop_changed",
                        "prefix": prefix,
                        "old": old[prefix]["next_hops"],
                        "new": new[prefix]["next_hops"],
                    }
                )

            if (
                old[prefix]["protocols"]
                != new[prefix]["protocols"]
            ):
                events.append(
                    {
                        "router": router,
                        "protocol": "route",
                        "event": "route_protocol_changed",
                        "prefix": prefix,
                        "old": old[prefix]["protocols"],
                        "new": new[prefix]["protocols"],
                    }
                )

    return events


def diff_snapshots(
    old_snapshot: dict,
    new_snapshot: dict
) -> list[dict]:
    
    old_state = normalize_snapshot(old_snapshot)
    new_state = normalize_snapshot(new_snapshot)

    old_routers = old_state["routers"]
    new_routers = new_state["routers"]

    events = []

    for router in sorted(set(old_routers) & set(new_routers)):
        if (
            old_routers[router].get("error")
            or new_routers[router].get("error")
        ):
            continue

        if (
            "ospf" in old_routers[router]
            and "ospf" in new_routers[router]
        ):
            events.extend(
                diff_ospf_neighbors(
                    router,
                    old_routers[router]["ospf"],
                    new_routers[router]["ospf"],
                )
            )

        if (
            "bgp" in old_routers[router]
            and "bgp" in new_routers[router]
        ):
            events.extend(
                diff_bgp_peers(
                    router,
                    old_routers[router]["bgp"],
                    new_routers[router]["bgp"],
                )
            )

        events.extend(
            diff_routes(
                router,
                old_routers[router].get("routes", {}),
                new_routers[router].get("routes", {}),
            )
        )

    return events


def main():
    parser = argparse.ArgumentParser(
        description="Compare two routing snapshots."
    )

    parser.add_argument("old_snapshot")
    parser.add_argument("new_snapshot")

    args = parser.parse_args()

    with open(
        args.old_snapshot,
        "r",
        encoding="utf-8"
    ) as file:
        old_snapshot = json.load(file)

    with open(
        args.new_snapshot,
        "r",
        encoding="utf-8"
    ) as file:
        new_snapshot = json.load(file)

    events = diff_snapshots(
        old_snapshot,
        new_snapshot
    )

    if events:
        print(f"{len(events)} event(s) detected:\n")

        for event in events:
            print(
                f"{event['router']} | "
                f"{event['protocol']} | "
                f"{event['event']}"
            )

    else:
        print("No routing changes detected.")

    events_dir = Path(
        "data/events"
    )

    events_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    output_file = (
        events_dir
        / f"change_{timestamp}.json"
    )

    output = {
        "old_snapshot": str(
            Path(args.old_snapshot)
        ),
        "new_snapshot": str(
            Path(args.new_snapshot)
        ),
        "events": events,
    }

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            output,
            file,
            indent=4
        )

    print(
        f"Event report saved to: {output_file}"
    )


if __name__ == "__main__":
    main()
