from calc_results._core import load_file, build_answers_map, build_votes_map, calc_results_map

from typing import Dict, List, Optional
import argparse

def main(argv: Optional[List[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Calculate poll results into point allocations")
    parser.add_argument("--poll-file", default="json_poll/poll_fab4d87b-747c-4127-bf26-419bb538147e.json")
    parser.add_argument("--results-file", default="live_results/results.json")
    parser.add_argument("--point-pool", type=int, default=100)

    args = parser.parse_args(argv)
    
    points_map = calc_results_map(args.poll_file, args.results_file, args.point_pool)



    print("\nPoints map (username -> points):")
    for k, v in points_map.items():
        print(f"- {k}: {v:.2f}")

if __name__ == "__main__":
    main()
