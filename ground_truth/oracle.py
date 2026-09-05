"""
Benchmark Oracle Engine
Provides rigorous, independent ground truth evaluation for:
- Sequence Reconstruction Accuracy (SRA) & Causal Inversion Rate
- Cross-Service Correlation Precision, Recall, F1, and Cross-Attacker Contamination
- Event-to-Attacker Attribution Accuracy
"""
import os
import json
from typing import Dict, List, Tuple, Any, Optional

class BenchmarkOracle:
    """
    Independent ground truth oracle for evaluating distributed honeypot benchmarks.
    Compares reconstructed sequences, clusters, and attributions against deterministic manifests.
    """

    def __init__(
        self,
        campaign_file: Optional[str] = None,
        labels_file: Optional[str] = None,
        order_file: Optional[str] = None,
        clusters_file: Optional[str] = None
    ):
        base_dir = os.path.dirname(__file__)
        self.campaign_file = campaign_file or os.path.join(base_dir, "campaigns", "campaign_001.json")
        self.labels_file = labels_file or os.path.join(base_dir, "event_labels", "labels_001.json")
        self.order_file = order_file or os.path.join(base_dir, "expected_order", "order_001.json")
        self.clusters_file = clusters_file or os.path.join(base_dir, "expected_correlations", "clusters_001.json")

        self.campaign = self._load_json(self.campaign_file)
        self.labels = self._load_json(self.labels_file).get("events", {})
        self.order_specs = self._load_json(self.order_file).get("causal_chains", {})
        cluster_data = self._load_json(self.clusters_file)
        self.expected_clusters = cluster_data.get("expected_clusters", [])
        self.disallowed_pairs = cluster_data.get("disallowed_pairs", [])

    @staticmethod
    def _load_json(path: str) -> dict:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Oracle manifest not found: {path}")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def evaluate_ordering(self, observed_sequence: List[str], actor_id: str = "ACTOR_ALPHA") -> Dict[str, Any]:
        """
        Evaluates sequence reconstruction accuracy against ground truth topological order.
        Calculates pairwise causal inversion rate, SRA, and Kendall's tau correlation.
        """
        chain = self.order_specs.get(actor_id, {})
        true_seq = chain.get("linear_sequence", [])
        if not true_seq:
            raise ValueError(f"Unknown actor_id or no sequence specified for {actor_id}")

        # Filter observed sequence to only contain events from this actor's ground truth
        filtered_obs = [eid for eid in observed_sequence if eid in true_seq]
        if not filtered_obs:
            return {
                "actor_id": actor_id,
                "sra": 0.0,
                "inversion_count": 0,
                "total_pairs": 0,
                "inversion_rate": 0.0,
                "kendall_tau": 0.0,
                "completeness": 0.0
            }

        true_rank_map = {eid: idx for idx, eid in enumerate(true_seq)}
        observed_ranks = [true_rank_map[eid] for eid in filtered_obs]

        # Calculate inversions among observed events
        inversions = 0
        total_pairs = 0
        n = len(observed_ranks)
        for i in range(n):
            for j in range(i + 1, n):
                total_pairs += 1
                if observed_ranks[i] > observed_ranks[j]:
                    inversions += 1

        inversion_rate = (inversions / total_pairs) if total_pairs > 0 else 0.0
        sra = 1.0 - inversion_rate

        # Simple Kendall tau rank correlation: (concordant - discordant) / total_pairs
        concordant = total_pairs - inversions
        kendall_tau = ((concordant - inversions) / total_pairs) if total_pairs > 0 else 1.0

        completeness = len(filtered_obs) / len(true_seq)

        return {
            "actor_id": actor_id,
            "sra": round(sra, 4),
            "inversion_count": inversions,
            "total_pairs": total_pairs,
            "inversion_rate": round(inversion_rate, 4),
            "kendall_tau": round(kendall_tau, 4),
            "completeness": round(completeness, 4)
        }

    def evaluate_correlation(self, predicted_clusters: List[List[str]], only_attack_clusters: bool = True) -> Dict[str, Any]:
        """
        Evaluates predicted clusters against ground truth event groupings using pairwise metrics.
        Computes True Positives, False Positives (over-clustering/contamination), False Negatives (under-clustering),
        Precision, Recall, F1 score, and checks disallowed cross-attacker pairs.
        """
        # Build ground truth pairwise co-membership set
        gt_pairs = set()
        all_gt_events = set()
        for cl in self.expected_clusters:
            if only_attack_clusters and not cl.get("is_attack", True):
                continue
            eids = cl.get("event_ids", [])
            for e in eids:
                all_gt_events.add(e)
            for i in range(len(eids)):
                for j in range(i + 1, len(eids)):
                    gt_pairs.add(tuple(sorted((eids[i], eids[j]))))

        # Build predicted pairwise co-membership set (only for events recognized by oracle)
        pred_pairs = set()
        for cl in predicted_clusters:
            filtered = [e for e in cl if e in all_gt_events]
            for i in range(len(filtered)):
                for j in range(i + 1, len(filtered)):
                    pred_pairs.add(tuple(sorted((filtered[i], filtered[j]))))

        tp = len(gt_pairs.intersection(pred_pairs))
        fp = len(pred_pairs.difference(gt_pairs))
        fn = len(gt_pairs.difference(pred_pairs))

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0.0
        f1 = (2 * precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0

        # Check cross-attacker contamination from disallowed pairs
        contaminated_pairs = []
        for p1, p2 in self.disallowed_pairs:
            pair_key = tuple(sorted((p1, p2)))
            if pair_key in pred_pairs:
                contaminated_pairs.append([p1, p2])

        return {
            "true_positives": tp,
            "false_positives": fp,
            "false_negatives": fn,
            "precision": round(precision, 4),
            "recall": round(recall, 4),
            "f1_score": round(f1, 4),
            "cross_attacker_contamination_count": len(contaminated_pairs),
            "contaminated_pairs": contaminated_pairs
        }

    def evaluate_attribution(self, predicted_actor_map: Dict[str, str]) -> Dict[str, Any]:
        """
        Evaluates event-to-actor attribution accuracy.
        predicted_actor_map: { "event_id": "PREDICTED_ACTOR_ID" }
        """
        total = 0
        correct = 0
        per_actor_stats: Dict[str, Dict[str, int]] = {}

        for eid, pred_actor in predicted_actor_map.items():
            if eid not in self.labels:
                continue
            true_actor = self.labels[eid]["actor_id"]
            total += 1

            if true_actor not in per_actor_stats:
                per_actor_stats[true_actor] = {"total": 0, "correct": 0}
            per_actor_stats[true_actor]["total"] += 1

            if pred_actor == true_actor:
                correct += 1
                per_actor_stats[true_actor]["correct"] += 1

        accuracy = (correct / total) if total > 0 else 0.0
        return {
            "total_evaluated_events": total,
            "correct_attributions": correct,
            "accuracy": round(accuracy, 4),
            "per_actor_breakdown": per_actor_stats
        }
