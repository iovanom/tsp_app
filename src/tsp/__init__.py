import argparse
import sys
import time

from tsp.algorithms.constructive import cheapest_insertion, nearest_neighbor, two_opt
from tsp.io.csv_reader import read_asymetric_matrix


def main() -> None:
    parser = argparse.ArgumentParser(description="Solve TSP using constructive algorithms")
    parser.add_argument("csv_file", help="Path to the CSV file containing the cost matrix")
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Starting node index (default: 0)"
    )
    parser.add_argument(
        "--algorithm",
        choices=["nearest_neighbor", "cheapest_insertion"],
        default="nearest_neighbor",
        help="Algorithm to use (default: nearest_neighbor)"
    )
    parser.add_argument(
        "--two-opt",
        action="store_true",
        help="Apply 2-opt improvement to the tour"
    )
    parser.add_argument(
        "--two-opt-max-passes",
        type=int,
        default=100,
        help="Max improvement passes for 2-opt (default: 100)"
    )
    parser.add_argument(
        "--two-opt-timeout",
        type=float,
        default=None,
        help="Timeout in seconds for 2-opt (default: no limit)"
    )
    parser.add_argument(
        "--benchmark",
        action="store_true",
        help="Run benchmark mode with multiple runs"
    )
    parser.add_argument(
        "--runs",
        type=int,
        default=10,
        help="Number of runs for benchmark (default: 10)"
    )
    args = parser.parse_args()

    try:
        graph = read_asymetric_matrix(args.csv_file)
        algos = {"nearest_neighbor": nearest_neighbor, "cheapest_insertion": cheapest_insertion}

        def get_tour_cost(start):
            tour, cost = algos[args.algorithm](graph, start)
            if args.two_opt:
                tour, cost = two_opt(graph, tour, max_passes=args.two_opt_max_passes, timeout=args.two_opt_timeout)
            return tour, cost

        if args.benchmark:
            costs = []
            times = []
            for _ in range(args.runs):
                start_time = time.time()
                tour, cost = get_tour_cost(args.start)
                end_time = time.time()
                costs.append(cost)
                times.append(end_time - start_time)
            algo_name = f"{args.algorithm}{' + 2-opt' if args.two_opt else ''}"
            print(f"Algorithm: {algo_name}")
            print(f"Runs: {args.runs}")
            print(f"Cost - Min: {min(costs):.2f}, Max: {max(costs):.2f}, Avg: {sum(costs)/len(costs):.2f}")
            print(f"Time - Min: {min(times):.4f}s, Max: {max(times):.4f}s, Avg: {sum(times)/len(times):.4f}s")
        else:
            tour, cost = get_tour_cost(args.start)
            tour_labels = [graph.labels[i] for i in tour]
            print(f"Tour: {tour_labels}")
            print(f"Cost: {cost}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
