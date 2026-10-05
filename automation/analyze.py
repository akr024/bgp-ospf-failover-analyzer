import argparse
import json


def analyze_results(results: list[dict]) -> None:
    scenario_times = {}

    for result in results:
        if not result["converged"]:
            continue

        scenario = result["scenario"]
        time_seconds = result["convergence_time_seconds"]

        scenario_times.setdefault(
            scenario,
            [],
        ).append(time_seconds)

    if not scenario_times:
        print("No successful convergence measurements found.")
        return

    print("\nConvergence Analysis")
    print("=" * 60)

    for scenario in sorted(scenario_times):
        times = scenario_times[scenario]

        minimum = min(times)
        maximum = max(times)
        average = sum(times) / len(times)
        value_range = maximum - minimum

        print(f"\nScenario: {scenario}")
        print(f"Runs: {len(times)}")
        print(f"Average: {average:.4f} s")
        print(f"Minimum: {minimum:.4f} s")
        print(f"Maximum: {maximum:.4f} s")
        print(f"Range:   {value_range:.4f} s")

    fastest_scenario = min(
        scenario_times,
        key=lambda scenario:
        sum(scenario_times[scenario])
        / len(scenario_times[scenario]),
    )

    fastest_average = (
        sum(scenario_times[fastest_scenario])
        / len(scenario_times[fastest_scenario])
    )

    print("\n" + "=" * 60)
    print("Comparison")
    print("=" * 60)

    for scenario in sorted(scenario_times):
        if scenario == fastest_scenario:
            continue

        average = (
            sum(scenario_times[scenario])
            / len(scenario_times[scenario])
        )

        difference = average - fastest_average

        print(
            f"{fastest_scenario} converged faster than "
            f"{scenario} by {difference:.4f} s"
        )

    print(
        f"\nFastest average: "
        f"{fastest_scenario} "
        f"({fastest_average:.4f} s)"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Analyze convergence experiment results."
    )

    parser.add_argument(
        "results_file",
        help="Path to a convergence results JSON file.",
    )

    args = parser.parse_args()

    with open(
        args.results_file,
        "r",
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    analyze_results(data["results"])


if __name__ == "__main__":
    main()
