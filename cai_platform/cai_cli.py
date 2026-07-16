#!/usr/bin/env python3
"""
CAI Command-Line Interface
Usage: python cai_cli.py analyze --cert-file data.csv --occupant-file occ.json
       python cai_cli.py predict --cert-file data.csv --occupant-file occ.json --system LEED --version v5 --target-tau 0.5
"""

import argparse
import json
import pandas as pd
from cai_core import CAIAnalyzer, CAIOptimizer
import sys

def load_data(cert_file, occupant_file):
    """Load certification and occupant data"""
    try:
        cert_data = pd.read_csv(cert_file)
    except Exception as e:
        print(f"Error loading cert file: {e}", file=sys.stderr)
        sys.exit(1)

    try:
        if occupant_file.endswith('.json'):
            with open(occupant_file) as f:
                occupant_data = json.load(f)
        else:
            occ_df = pd.read_csv(occupant_file)
            occupant_data = dict(zip(occ_df['topic'], occ_df['dissatisfaction_pct']))
    except Exception as e:
        print(f"Error loading occupant file: {e}", file=sys.stderr)
        sys.exit(1)

    return cert_data, occupant_data


def cmd_analyze(args):
    """Run analysis command"""
    print("Loading data...")
    cert_data, occupant_data = load_data(args.cert_file, args.occupant_file)

    print("Analyzing alignment...")
    analyzer = CAIAnalyzer(cert_data, occupant_data)
    results = analyzer.analyze()

    print("\n" + "="*80)
    print("CAI ANALYSIS RESULTS")
    print("="*80)

    # Summary
    summary = analyzer.get_summary()
    print(f"\nSummary Statistics:")
    print(f"   Systems analyzed: {summary['n_systems']}")
    print(f"   Versions analyzed: {summary['n_versions']}")
    print(f"   Time span: {summary['years_span']}")
    print(f"   Average alignment (τ): {summary['avg_tau']:.3f}")
    print(f"   Range: {summary['min_tau']:.3f} to {summary['max_tau']:.3f}")

    # Results table
    print(f"\nDetailed Results:")
    display_cols = ['System', 'Version', 'Year', 'Tau', 'CI_Lower', 'CI_Upper', 'Spearman_Rho']
    print(results[display_cols].to_string(index=False))

    # Gaps
    print(f"\nTopic-Level Gaps (Cert% - Occupant%):")
    gaps = analyzer.get_gaps_by_topic()
    for topic, gap_info in gaps.items():
        gap = gap_info['avg_gap']
        direction = "OVER" if gap > 0 else "UNDER"
        print(f"   {topic:12s}: {gap:+6.1f}% gap ({direction}-allocated)")
        print(f"                Occupant: {gap_info['occupant_pct']:.0f}%, Cert avg: {gap_info['cert_pct']:.1f}%")

    # Save results
    if args.output:
        results.to_csv(args.output, index=False)
        print(f"\nResults saved to {args.output}")

    print("\n" + "="*80)


def cmd_predict(args):
    """Run prediction/optimization command"""
    print("Loading data...")
    cert_data, occupant_data = load_data(args.cert_file, args.occupant_file)

    print(f"Optimizing {args.system} {args.version} toward target tau = {args.target_tau}...")
    optimizer = CAIOptimizer(cert_data, occupant_data, args.system, args.version)

    result = optimizer.predict(target_tau=args.target_tau)

    print("\n" + "="*80)
    print(f"CAI OPTIMIZATION: {args.system} {args.version}")
    print("="*80)

    print(f"\nCurrent Alignment:")
    print(f"   Kendall τ: {result['current_tau']:.3f}")
    print(f"   Target τ:  {args.target_tau:.3f}")
    print(f"   Gap:       {args.target_tau - result['current_tau']:.3f}")

    print(f"\nOptimized Allocation:")
    print(f"   New τ:     {result['optimized_tau']:.3f}")
    print(f"   Improvement: {result['tau_improvement']:+.3f}")

    print(f"\nRecommended Point Reallocation:")
    print(f"{'Topic':<15} {'Current':>10} {'Optimized':>10} {'Change':>10}")
    print("-" * 50)
    for topic in result['topics']:
        current = result['current_allocation'][topic]
        optimized = result['optimized_allocation'][topic]
        change_pct = result['percent_change'][topic]
        print(f"{topic:<15} {current:>10} {optimized:>10} {change_pct:>+9.0f}%")

    # Suggested reallocation alternative
    print(f"\nAlternative: Gap-Based Reallocation (close 50% of gap):")
    suggested = optimizer.suggest_reallocation(target_gap_reduction=0.5)
    print(f"{'Topic':<15} {'Current':>10} {'Suggested':>10} {'Change':>10}")
    print("-" * 50)
    for topic in suggested['topics']:
        current = suggested['current_allocation'][topic]
        sugg = suggested['suggested_allocation'][topic]
        change_pct = suggested['percent_change'][topic]
        print(f"{topic:<15} {current:>10} {sugg:>10} {change_pct:>+9.0f}%")

    # Save results
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2, default=str)
        print(f"\nResults saved to {args.output}")

    print("\n" + "="*80)


def main():
    parser = argparse.ArgumentParser(
        description='CAI Platform: Certification-Occupant Alignment Analysis & Optimization'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Analyze command
    analyze_parser = subparsers.add_parser('analyze', help='Analyze alignment across systems')
    analyze_parser.add_argument('--cert-file', required=True, help='CSV file with certification data')
    analyze_parser.add_argument('--occupant-file', required=True, help='JSON/CSV with occupant priorities')
    analyze_parser.add_argument('--output', help='Output CSV file for results')
    analyze_parser.set_defaults(func=cmd_analyze)

    # Predict command
    predict_parser = subparsers.add_parser('predict', help='Predict optimal cert allocations')
    predict_parser.add_argument('--cert-file', required=True, help='CSV file with certification data')
    predict_parser.add_argument('--occupant-file', required=True, help='JSON/CSV with occupant priorities')
    predict_parser.add_argument('--system', required=True, help='Certification system (e.g., LEED)')
    predict_parser.add_argument('--version', required=True, help='System version (e.g., v5)')
    predict_parser.add_argument('--target-tau', type=float, default=0.0, help='Target τ value (default: 0.0)')
    predict_parser.add_argument('--output', help='Output JSON file for results')
    predict_parser.set_defaults(func=cmd_predict)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    args.func(args)


if __name__ == '__main__':
    main()
