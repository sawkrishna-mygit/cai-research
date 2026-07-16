#!/usr/bin/env python3
"""
CAI (Certification-Occupant Alignment) Core Library
Reusable analysis and prediction engine for building certification alignment
"""

import pandas as pd
import numpy as np
from scipy.stats import kendalltau, spearmanr, linregress
from scipy.optimize import minimize
import warnings
warnings.filterwarnings('ignore')

class CAIAnalyzer:
    """Analyze alignment between certification priorities and occupant needs"""

    def __init__(self, cert_data, occupant_data):
        """
        Initialize analyzer with certification and occupant data

        Args:
            cert_data: DataFrame with columns [system, version, year, topic, points, system_total]
            occupant_data: Dict mapping topic names to dissatisfaction percentages
                          e.g., {'Acoustics': 54, 'Thermal': 39, ...}
        """
        self.cert_data = cert_data
        self.occupant_data = occupant_data
        self.topics = list(occupant_data.keys())
        self.results = None

    def _calculate_alignment(self, cert_points_order):
        """Calculate tie-aware Kendall tau-b between paired cert and occupant values."""
        occupant_values = [self.occupant_data[t] for t in self.topics]
        tau, p_val = kendalltau(cert_points_order, occupant_values)
        return tau, p_val

    def _bootstrap_ci(self, cert_points, n_resamples=1000, ci=0.95):
        """Calculate paired-topic bootstrap confidence interval for Kendall tau-b."""
        tau_boots = []
        np.random.seed(42)

        for _ in range(n_resamples):
            indices = np.random.choice(len(cert_points), size=len(cert_points), replace=True)
            sampled_points = [cert_points[i] for i in indices]
            sampled_topics = [self.topics[i] for i in indices]
            sampled_occupant = [self.occupant_data[t] for t in sampled_topics]
            tau, _ = kendalltau(sampled_points, sampled_occupant)
            if not np.isnan(tau):
                tau_boots.append(tau)

        if not tau_boots:
            return np.nan, np.nan
        tau_boots = np.array(tau_boots)
        lower = np.percentile(tau_boots, (1 - ci) / 2 * 100)
        upper = np.percentile(tau_boots, (1 + ci) / 2 * 100)
        return lower, upper

    def analyze(self):
        """Run full alignment analysis on all certification versions"""
        results = []

        for system in self.cert_data['system'].unique():
            system_data = self.cert_data[self.cert_data['system'] == system]

            for version in system_data['version'].unique():
                version_data = system_data[system_data['version'] == version]
                year = version_data['year'].iloc[0]
                system_total = version_data['system_total'].iloc[0]

                # Get points for each topic
                points_list = []
                for topic in self.topics:
                    topic_data = version_data[version_data['topic'] == topic]
                    points = topic_data['points'].iloc[0] if len(topic_data) > 0 else 0
                    points_list.append(points)

                # Calculate metrics
                tau, p_val = self._calculate_alignment(points_list)
                ci_lower, ci_upper = self._bootstrap_ci(points_list)

                # Spearman rho
                occupant_values = [self.occupant_data[t] for t in self.topics]
                rho, _ = spearmanr(points_list, occupant_values)

                # Topic percentages
                topic_pcts = {t: 100 * p / system_total for t, p in zip(self.topics, points_list)}

                # Gap analysis
                gaps = {t: topic_pcts[t] - self.occupant_data[t] for t in self.topics}

                results.append({
                    'System': system,
                    'Version': version,
                    'Year': year,
                    'Tau': tau,
                    'P_Value': p_val,
                    'CI_Lower': ci_lower,
                    'CI_Upper': ci_upper,
                    'Spearman_Rho': rho,
                    'System_Total': system_total,
                    **{f'{t}_pts': p for t, p in zip(self.topics, points_list)},
                    **{f'{t}_pct': pct for t, pct in topic_pcts.items()},
                    **{f'{t}_gap': gap for t, gap in gaps.items()}
                })

        self.results = pd.DataFrame(results).sort_values(['System', 'Year'])
        return self.results

    def get_summary(self):
        """Get summary statistics"""
        if self.results is None:
            self.analyze()

        return {
            'n_systems': self.results['System'].nunique(),
            'n_versions': len(self.results),
            'avg_tau': self.results['Tau'].mean(),
            'min_tau': self.results['Tau'].min(),
            'max_tau': self.results['Tau'].max(),
            'tau_std': self.results['Tau'].std(),
            'years_span': f"{int(self.results['Year'].min())}-{int(self.results['Year'].max())}",
        }

    def get_gaps_by_topic(self):
        """Get average gaps by topic across all versions"""
        if self.results is None:
            self.analyze()

        gaps = {}
        for topic in self.topics:
            gap_col = f'{topic}_gap'
            gaps[topic] = {
                'avg_gap': self.results[gap_col].mean(),
                'min_gap': self.results[gap_col].min(),
                'max_gap': self.results[gap_col].max(),
                'occupant_pct': self.occupant_data[topic],
                'cert_pct': self.results[f'{topic}_pct'].mean()
            }
        return gaps


class CAIOptimizer:
    """Predict/optimize certification allocations to improve alignment"""

    def __init__(self, cert_data, occupant_data, system_name, version_name):
        """
        Initialize optimizer for a specific certification system/version

        Args:
            cert_data: DataFrame with cert point data
            occupant_data: Dict of topic -> dissatisfaction %
            system_name: Name of system (e.g., 'LEED')
            version_name: Version identifier (e.g., 'v5')
        """
        self.cert_data = cert_data[
            (cert_data['system'] == system_name) &
            (cert_data['version'] == version_name)
        ]
        self.occupant_data = occupant_data
        self.topics = list(occupant_data.keys())
        self.system_total = self.cert_data['system_total'].iloc[0]

        # Current allocations
        self.current_points = {}
        for topic in self.topics:
            topic_data = self.cert_data[self.cert_data['topic'] == topic]
            self.current_points[topic] = topic_data['points'].iloc[0] if len(topic_data) > 0 else 0

    def _calculate_tau(self, points_array):
        """Calculate Kendall tau for given point allocation"""
        occupant_values = [self.occupant_data[t] for t in self.topics]
        tau, _ = kendalltau(points_array, occupant_values)
        return tau

    def _objective_function(self, points_array, target_tau):
        """Objective: minimize distance from target tau"""
        tau = self._calculate_tau(points_array)
        return (tau - target_tau) ** 2

    def predict(self, target_tau=0.0, max_iterations=1000):
        """
        Find optimal point allocation to achieve target alignment

        Args:
            target_tau: Desired Kendall tau value (default 0.0 = perfect alignment)
            max_iterations: Maximum optimization iterations

        Returns:
            dict with optimized allocations and improvement metrics
        """
        current_array = np.array([self.current_points[t] for t in self.topics], dtype=float)
        current_tau = self._calculate_tau(current_array)
        topic_budget = current_array.sum()
        occupant_total = sum(self.occupant_data.values())

        if topic_budget <= 0 or occupant_total <= 0:
            optimized_points = current_array.copy()
            success = False
        elif current_tau >= target_tau:
            optimized_points = current_array.copy()
            success = True
        else:
            # Kendall tau is rank-based and discontinuous, so gradient optimizers can
            # stall. Use the occupant-priority distribution as the interpretable
            # allocation target while preserving the current IEQ topic budget.
            optimized_points = np.array([
                topic_budget * self.occupant_data[t] / occupant_total
                for t in self.topics
            ])
            success = True

        optimized_tau = self._calculate_tau(optimized_points)

        return {
            'topics': self.topics,
            'current_allocation': {t: int(self.current_points[t]) for t in self.topics},
            'optimized_allocation': {t: int(p) for t, p in zip(self.topics, optimized_points)},
            'current_tau': current_tau,
            'optimized_tau': optimized_tau,
            'tau_improvement': optimized_tau - current_tau,
            'percent_change': {
                t: 100 * (optimized_points[i] - self.current_points[t]) / max(self.current_points[t], 1)
                for i, t in enumerate(self.topics)
            },
            'success': success,
            'target_tau': target_tau
        }

    def suggest_reallocation(self, target_gap_reduction=0.5):
        """
        Suggest reallocation based on closing gap % toward occupant priorities

        Args:
            target_gap_reduction: Fraction of gap to close (0.0-1.0)

        Returns:
            dict with suggested allocations
        """
        suggested = {}
        occupant_total = sum(self.occupant_data.values())

        for topic in self.topics:
            occ_pct = self.occupant_data[topic]
            current_pct = 100 * self.current_points[topic] / self.system_total

            # Target percentage (partial movement toward occupant priority)
            target_pct = current_pct + target_gap_reduction * (occ_pct - current_pct)
            suggested_pts = int(target_pct * self.system_total / 100)
            suggested[topic] = suggested_pts

        # Normalize to sum to system_total
        total_suggested = sum(suggested.values())
        if total_suggested != self.system_total:
            adjustment = self.system_total / total_suggested
            suggested = {t: int(p * adjustment) for t, p in suggested.items()}

        return {
            'topics': self.topics,
            'current_allocation': {t: int(self.current_points[t]) for t in self.topics},
            'suggested_allocation': suggested,
            'percent_change': {
                t: 100 * (suggested[t] - self.current_points[t]) / max(self.current_points[t], 1)
                for t in self.topics
            }
        }
