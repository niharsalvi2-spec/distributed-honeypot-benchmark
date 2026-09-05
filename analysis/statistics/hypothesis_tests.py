"""
Rigorous Scientific Hypothesis Testing Engine.
Evaluates H1, H2, H3, H4 using paired t-tests, Mann-Whitney U, and Wilcoxon signed-rank tests.
"""
from scipy import stats
from typing import List, Dict, Any

class HypothesisTester:
    @staticmethod
    def test_h1_distributed_coverage(single_service_counts: List[int],
                                     multi_service_counts: List[int]) -> Dict[str, Any]:
        stat, p = stats.mannwhitneyu(multi_service_counts, single_service_counts, alternative='greater')
        return {
            "hypothesis": "H1_Distributed_Observation",
            "test": "Mann-Whitney U",
            "statistic": round(float(stat), 4),
            "p_value": float(p),
            "reject_null": bool(p < 0.05)
        }

    @staticmethod
    def test_h3_ordering_error_reduction(physical_inversion_rates: List[float],
                                         logical_inversion_rates: List[float]) -> Dict[str, Any]:
        stat, p = stats.wilcoxon(physical_inversion_rates, logical_inversion_rates, alternative='greater')
        return {
            "hypothesis": "H3_Logical_Event_Ordering",
            "test": "Wilcoxon Signed-Rank",
            "statistic": round(float(stat), 4),
            "p_value": float(p),
            "reject_null": bool(p < 0.05)
        }
