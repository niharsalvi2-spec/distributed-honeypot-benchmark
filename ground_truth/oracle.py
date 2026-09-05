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
        composite_sequence_score = round(sra * completeness, 4)

        return {
            "actor_id": actor_id,
            "sra": round(sra, 4),
            "completeness": round(completeness, 4),
            "composite_sequence_score": composite_sequence_score,
            "inversion_count": inversions,
            "total_pairs": total_pairs,
            "inversion_rate": round(inversion_rate, 4),
            "kendall_tau": round(kendall_tau, 4)
        }

    def evaluate_partial_order(
        self,
        predicted_relations: Dict[Tuple[str, str], str],
        actor_id: str = "ACTOR_ALPHA",
        true_sequence: Optional[List[str]] = None,
        causal_dag: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates predicted partial order relations (BEFORE, AFTER, CONCURRENT, EQUAL)
        against true causal DAG reachability semantics using NetworkX:
        - u ->* v (directed path exists): BEFORE
        - v ->* u (directed path exists): AFTER
        - u == v: EQUAL
        - neither path exists: CONCURRENT (u || v)
        """
        import networkx as nx
        chain = causal_dag or self.order_specs.get(actor_id, {})
        nodes = chain.get("nodes") or true_sequence or chain.get("linear_sequence", [])
        causal_edges = chain.get("causal_edges") or chain.get("edges", [])

        # Construct NetworkX DiGraph representing true causal happens-before relations
        G = nx.DiGraph()
        G.add_nodes_from(nodes)
        for edge in causal_edges:
            G.add_edge(edge["from"], edge["to"])

        # If no explicit edges were provided but a linear sequence exists, treat as linear total order
        if len(causal_edges) == 0 and len(nodes) > 1:
            for i in range(len(nodes) - 1):
                G.add_edge(nodes[i], nodes[i+1])

        total_evaluated = 0
        correct_relations = 0
        concurrency_tp = 0
        concurrency_fp = 0
        concurrency_fn = 0
        gt_concurrent_count = 0

        for pair, pred_rel in predicted_relations.items():
            u, v = pair
            if not G.has_node(u) or not G.has_node(v):
                continue
            total_evaluated += 1

            if u == v:
                expected_rel = "EQUAL"
            elif nx.has_path(G, u, v):
                expected_rel = "BEFORE"
            elif nx.has_path(G, v, u):
                expected_rel = "AFTER"
            else:
                expected_rel = "CONCURRENT"

            if expected_rel == "CONCURRENT":
                gt_concurrent_count += 1

            if pred_rel == expected_rel:
                correct_relations += 1

            if pred_rel == "CONCURRENT" and expected_rel == "CONCURRENT":
                concurrency_tp += 1
            elif pred_rel == "CONCURRENT" and expected_rel != "CONCURRENT":
                concurrency_fp += 1
            elif pred_rel != "CONCURRENT" and expected_rel == "CONCURRENT":
                concurrency_fn += 1

        accuracy = (correct_relations / total_evaluated) if total_evaluated > 0 else 1.0
        conc_prec = concurrency_tp / (concurrency_tp + concurrency_fp) if (concurrency_tp + concurrency_fp) > 0 else 1.0
        conc_rec = concurrency_tp / (concurrency_tp + concurrency_fn) if (concurrency_tp + concurrency_fn) > 0 else 1.0
        conc_f1 = (2 * conc_prec * conc_rec) / (conc_prec + conc_rec) if (conc_prec + conc_rec) > 0 else 1.0

        return {
            "actor_id": actor_id,
            "total_evaluated_pairs": total_evaluated,
            "correct_relations": correct_relations,
            "relation_accuracy": round(accuracy, 4),
            "concurrency_metrics": {
                "ground_truth_concurrent_pairs": gt_concurrent_count,
                "true_positives": concurrency_tp,
                "false_positives": concurrency_fp,
                "false_negatives": concurrency_fn,
                "precision": round(conc_prec, 4),
                "recall": round(conc_rec, 4),
                "f1_score": round(conc_f1, 4)
            }
        }

    def evaluate_correlation(
        self,
        predicted_clusters: List[List[str]],
        only_attack_clusters: bool = True,
        custom_gt_clusters: Optional[Dict[str, List[str]]] = None
    ) -> Dict[str, Any]:
        """
        Evaluates predicted clusters against ground truth event groupings using pairwise metrics.
        Computes True Positives, False Positives (over-clustering/contamination), False Negatives (under-clustering),
        Precision, Recall, F1 score, and checks disallowed cross-attacker pairs.
        Supports both pre-defined JSON oracle specs and dynamic custom_gt_clusters from ScenarioGenerator.
        """
        # Build ground truth pairwise co-membership set
        gt_pairs = set()
        all_gt_events = set()
        disallowed = set()

        if custom_gt_clusters:
            for actor, eids in custom_gt_clusters.items():
                for e in eids:
                    all_gt_events.add(e)
                for i in range(len(eids)):
                    for j in range(i + 1, len(eids)):
                        gt_pairs.add(tuple(sorted((eids[i], eids[j]))))
            actors = list(custom_gt_clusters.keys())
            for i in range(len(actors)):
                for j in range(i + 1, len(actors)):
                    for e1 in custom_gt_clusters[actors[i]]:
                        for e2 in custom_gt_clusters[actors[j]]:
                            disallowed.add(tuple(sorted((e1, e2))))
        else:
            for cl in self.expected_clusters:
                if only_attack_clusters and not cl.get("is_attack", True):
                    continue
                eids = cl.get("event_ids", [])
                for e in eids:
                    all_gt_events.add(e)
                for i in range(len(eids)):
                    for j in range(i + 1, len(eids)):
                        gt_pairs.add(tuple(sorted((eids[i], eids[j]))))
            disallowed = {tuple(sorted((p1, p2))) for p1, p2 in self.disallowed_pairs}

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
        for pair_key in disallowed:
            if pair_key in pred_pairs:
                contaminated_pairs.append(list(pair_key))

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
