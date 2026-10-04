import argparse
from getpass import getpass

from devices import FAILURE_SCENARIOS, ROUTERS
from ssh_client import run_command


def set_interface_state(
    host: str,
    username: str,
    password: str,
    interface: str,
    enabled: bool,
) -> str:
    if enabled:
        state_command = "no shutdown"
    else:
        state_command = "shutdown"

    command = (
        'vtysh '
        '-c "configure terminal" '
        f'-c "interface {interface}" '
        f'-c "{state_command}" '
        '-c "end"'
    )

    return run_command(
        host=host,
        username=username,
        password=password,
        command=command,
    )


def shutdown_interface(
    host: str,
    username: str,
    password: str,
    interface: str,
) -> str:
    return set_interface_state(
        host=host,
        username=username,
        password=password,
        interface=interface,
        enabled=False,
    )


def restore_interface(
    host: str,
    username: str,
    password: str,
    interface: str,
) -> str:

    return set_interface_state(
        host=host,
        username=username,
        password=password,
        interface=interface,
        enabled=True,
    )


def set_failure_scenario(
    scenario: str,
    username: str,
    password: str,
    down: bool,
) -> str:
    if scenario not in FAILURE_SCENARIOS:
        raise ValueError(
            f"Unknown failure scenario: {scenario}"
        )

    scenario_info = FAILURE_SCENARIOS[scenario]

    router_name = scenario_info["router"]
    interface = scenario_info["interface"]

    if router_name not in ROUTERS:
        raise ValueError(
            f"Router '{router_name}' is not defined in ROUTERS"
        )

    router_info = ROUTERS[router_name]
    host = router_info["host"]

    if down:
        return shutdown_interface(
            host=host,
            username=username,
            password=password,
            interface=interface,
        )

    return restore_interface(
        host=host,
        username=username,
        password=password,
        interface=interface,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Inject or restore a network failure."
    )

    parser.add_argument(
        "action",
        choices=["down", "up"],
        help="Whether to shut down or restore the interface.",
    )

    parser.add_argument(
        "scenario",
        choices=sorted(FAILURE_SCENARIOS),
        help="Failure scenario to execute.",
    )

    args = parser.parse_args()

    username = "root"
    password = getpass("SSH Password: ")

    down = args.action == "down"

    print(
        f"{'Injecting' if down else 'Restoring'} "
        f"failure scenario '{args.scenario}'..."
    )

    output = set_failure_scenario(
        scenario=args.scenario,
        username=username,
        password=password,
        down=down,
    )

    if output:
        print(output)


if __name__ == "__main__":
    main()
