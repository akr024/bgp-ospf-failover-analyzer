import argparse
import json
import time
from datetime import datetime, timezone
from getpass import getpass
from pathlib import Path

from devices import (
    CONVERGENCE_SCENARIOS,
    ROUTE_COMMAND,
    ROUTERS,
)
from failure_injection import set_failure_scenario
from ssh_client import run_command
from state import normalize_routes


DEFAULT_TIMEOUT = 10.0
DEFAULT_POLL_INTERVAL = 0.2
DEFAULT_STABLE_POLLS = 2


def get_route_next_hops(
    router_name: str,
    password: str,
    prefix: str,
) -> list[str]:
    if router_name not in ROUTERS:
        raise ValueError(
            f"Unknown router: {router_name}"
        )

    device = ROUTERS[router_name]

    output = run_command(
        host=device["host"],
        username="root",
        password=password,
        command=ROUTE_COMMAND,
    )

    raw_routes = json.loads(output)
    routes = normalize_routes(raw_routes)

    route = routes.get(prefix)

    if route is None:
        return []

    return route["next_hops"]


def run_scenario(
    scenario_name: str,
    password: str,
    timeout: float,
    interval: float,
    stable_polls_required: int,
) -> dict:
    if scenario_name not in CONVERGENCE_SCENARIOS:
        raise ValueError(
            f"Unknown convergence scenario: "
            f"{scenario_name}"
        )

    scenario = CONVERGENCE_SCENARIOS[scenario_name]

    monitor = scenario["monitor"]
    prefix = scenario["prefix"]
    failed_next_hop = scenario["failed_next_hop"]

    print(f"\n=== {scenario_name} ===")
    print(f"Monitor: {monitor}")
    print(f"Prefix: {prefix}")
    print(f"Failed next-hop: {failed_next_hop}")

    baseline_next_hops = get_route_next_hops(
        router_name=monitor,
        password=password,
        prefix=prefix,
    )

    print(
        f"Baseline next-hops: {baseline_next_hops}"
    )

    if failed_next_hop not in baseline_next_hops:
        raise RuntimeError(
            f"{failed_next_hop} is not currently "
            f"being used by {monitor} for {prefix}. "
            f"Current next-hops: {baseline_next_hops}"
        )

    try:
        print("Injecting failure...")

        set_failure_scenario(
            scenario=scenario_name,
            username="root",
            password=password,
            down=True,
        )

        failure_time = time.monotonic()

        print("Failure injected.")
        print("Measuring convergence...")

        stable_polls = 0
        convergence_time = None
        final_next_hops = None

        deadline = failure_time + timeout

        while time.monotonic() < deadline:

            current_next_hops = get_route_next_hops(
                router_name=monitor,
                password=password,
                prefix=prefix,
            )

            if (
                current_next_hops
                and current_next_hops != baseline_next_hops
                and failed_next_hop not in current_next_hops
            ):
                stable_polls += 1

                if convergence_time is None:
                    convergence_time = (
                        time.monotonic()
                        - failure_time
                    )

                if stable_polls >= stable_polls_required:
                    final_next_hops = current_next_hops
                    break

            else:
                stable_polls = 0
                convergence_time = None

            time.sleep(interval)

        converged = final_next_hops is not None

        result = {
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat(),
            "scenario": scenario_name,
            "monitor": monitor,
            "prefix": prefix,
            "failed_next_hop": failed_next_hop,
            "baseline_next_hops": baseline_next_hops,
            "final_next_hops": final_next_hops,
            "converged": converged,
            "convergence_time_seconds": (
                convergence_time
                if converged
                else None
            ),
            "poll_interval_seconds": interval,
            "stable_polls_required": (
                stable_polls_required
            ),
        }

        if converged:
            print(
                "Converged: True"
            )
            print(
                f"Convergence time: "
                f"{convergence_time:.4f}s"
            )
            print(
                f"Final next-hops: "
                f"{final_next_hops}"
            )
        else:
            print(
                "Converged: False"
            )
            print(
                f"No convergence detected within "
                f"{timeout:.1f}s."
            )

        return result

    finally:
        print("Restoring failure scenario...")

        set_failure_scenario(
            scenario=scenario_name,
            username="root",
            password=password,
            down=False,
        )

        print("Failure scenario restored.")


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Measure routing convergence after "
            "a controlled network failure."
        )
    )

    parser.add_argument(
        "scenario",
        choices=[
            "all",
            *sorted(CONVERGENCE_SCENARIOS),
        ],
    )

    parser.add_argument(
        "--runs",
        type=int,
        default=1,
        help="Number of runs per scenario.",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=DEFAULT_TIMEOUT,
        help="Maximum convergence wait time.",
    )

    parser.add_argument(
        "--interval",
        type=float,
        default=DEFAULT_POLL_INTERVAL,
        help="Time between route polls.",
    )

    parser.add_argument(
        "--stable-polls",
        type=int,
        default=DEFAULT_STABLE_POLLS,
        help=(
            "Consecutive converged polls required "
            "before declaring success."
        ),
    )

    args = parser.parse_args()

    if args.runs < 1:
        parser.error(
            "--runs must be at least 1"
        )

    if args.timeout <= 0:
        parser.error(
            "--timeout must be greater than 0"
        )

    if args.interval <= 0:
        parser.error(
            "--interval must be greater than 0"
        )

    if args.stable_polls < 1:
        parser.error(
            "--stable-polls must be at least 1"
        )

    password = getpass("SSH Password: ")

    if args.scenario == "all":
        scenarios = sorted(
            CONVERGENCE_SCENARIOS
        )
    else:
        scenarios = [args.scenario]

    results = []

    for scenario_name in scenarios:

        for run_number in range(
            1,
            args.runs + 1,
        ):
            print(
                f"\nRun {run_number}/{args.runs}"
            )

            result = run_scenario(
                scenario_name=scenario_name,
                password=password,
                timeout=args.timeout,
                interval=args.interval,
                stable_polls_required=(
                    args.stable_polls
                ),
            )

            result["run"] = run_number

            results.append(result)

    output_directory = (
        Path(__file__).resolve().parent.parent
        / "data"
        / "convergence"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    timestamp = datetime.now(
        timezone.utc
    ).strftime(
        "%Y%m%dT%H%M%S%fZ"
    )

    output_file = (
        output_directory
        / f"convergence_{timestamp}.json"
    )

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as file:
        json.dump(
            {"results": results},
            file,
            indent=4,
        )

    print(
        f"\nResults saved to: {output_file}"
    )


if __name__ == "__main__":
    main()
