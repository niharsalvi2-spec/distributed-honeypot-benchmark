"""
Dynamic Campaign & Synthetic Scenario Generator
Generates full reproducible attack scenarios with independent ground truth manifests
for evaluation against the BenchmarkOracle.
"""
import uuid
import random
from typing import Dict, Any, List, Tuple
from ground_truth.generator.causal_graph_generator import CausalGraphGenerator
from ground_truth.generator.clock_skew_generator import ClockSkewGenerator

class CampaignGenerator:
    """
    Generates dynamic multi-stage distributed attack campaigns with controllable parameters:
    - num_nodes: number of honeypot nodes
    - num_actors: distinct threat actors
    - stages_per_actor: depth of attack chain
    - noise_ratio: proportion of benign background scans
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        random.seed(seed)

    def generate(
        self,
        num_nodes: int = 3,
        num_actors: int = 2,
        noise_events_count: int = 4,
        max_clock_skew: float = 3.0
    ) -> Dict[str, Any]:
        nodes = [f"node-{i+1}" for i in range(num_nodes)]
        services = ["HTTP", "SSH", "SMB", "FTP", "MSSQL"]
        
        events = []
        labels = {}
        dag_gen = CausalGraphGenerator()
        expected_clusters = []
        disallowed_pairs = []

        base_time = 1700000000.0

        for a_idx in range(num_actors):
            actor_id = f"ACTOR_{chr(65 + a_idx)}"
            actor_ip = f"198.51.{100 + a_idx}.{random.randint(10, 200)}"
            internal_pivot_ip = f"192.168.10.{random.randint(2, 50)}"
            causal_token = f"token-jump-pivot-{uuid.uuid4().hex[:6]}"

            actor_events = []
            stages = ["RECON", "AUTH", "EXEC", "UPLOAD", "PIVOT_SMB", "PAYLOAD_DROP"]

            for s_idx, stage in enumerate(stages):
                eid = f"evt-{actor_id.lower()}-{s_idx+1:03d}"
                node = nodes[0] if s_idx < 4 else nodes[min(1, len(nodes) - 1)]
                service = services[s_idx % len(services)]
                
                # IP shifts from external to internal on lateral pivot
                src_ip = actor_ip if s_idx < 4 else internal_pivot_ip
                tok = causal_token if s_idx >= 2 else None
                event_ts = base_time + (a_idx * 15.0) + (s_idx * 60.0)

                ev_record = {
                    "event_id": eid,
                    "timestamp": event_ts,
                    "source_ip": src_ip,
                    "target_node": node,
                    "service": service,
                    "event_type": f"stage_{stage.lower()}",
                    "payload": f"STAGE_{stage} payload on {service}",
                    "causal_token": tok
                }
                events.append(ev_record)
                actor_events.append(eid)

                labels[eid] = {
                    "actor_id": actor_id,
                    "source_ip": src_ip,
                    "target_node": node,
                    "service": service,
                    "stage": stage,
                    "true_sequence_rank": s_idx + 1
                }

                dag_gen.add_event(eid, node, service, stage, actor_id)
                if s_idx > 0:
                    prev_eid = actor_events[s_idx - 1]
                    dag_gen.add_causal_edge(prev_eid, eid, f"chain_{s_idx}")

            expected_clusters.append({
                "cluster_id": f"CLUSTER_{actor_id}",
                "actor_id": actor_id,
                "is_attack": True,
                "event_ids": actor_events
            })

        # Add benign background noise
        noise_events = []
        for n_idx in range(noise_events_count):
            neid = f"evt-noise-{n_idx+1:03d}"
            noise_ip = f"198.18.0.{random.randint(1, 254)}"
            node = random.choice(nodes)
            service = random.choice(services)
            ev_record = {
                "event_id": neid,
                "timestamp": base_time + random.uniform(0, 360),
                "source_ip": noise_ip,
                "target_node": node,
                "service": service,
                "event_type": "noise_probe",
                "payload": f"SCAN /robots.txt on {service}",
                "causal_token": None
            }
            events.append(ev_record)
            noise_events.append(neid)
            labels[neid] = {
                "actor_id": "BENIGN_NOISE",
                "source_ip": noise_ip,
                "target_node": node,
                "service": service,
                "stage": "NOISE",
                "true_sequence_rank": None
            }

        expected_clusters.append({
            "cluster_id": "CLUSTER_NOISE",
            "actor_id": "BENIGN_NOISE",
            "is_attack": False,
            "event_ids": noise_events
        })

        # Build disallowed pairs across distinct actors
        for i in range(len(expected_clusters)):
            for j in range(i + 1, len(expected_clusters)):
                if expected_clusters[i]["is_attack"] and expected_clusters[j]["is_attack"]:
                    e_i = expected_clusters[i]["event_ids"][0]
                    e_j = expected_clusters[j]["event_ids"][0]
                    disallowed_pairs.append([e_i, e_j])

        # Apply clock skew
        skew_gen = ClockSkewGenerator(max_skew_sec=max_clock_skew, seed=self.seed)
        skewed_events = skew_gen.apply_skew(events)

        return {
            "unannotated_telemetry": events,
            "skewed_telemetry": skewed_events,
            "ground_truth_labels": {"events": labels},
            "ground_truth_clusters": {
                "expected_clusters": expected_clusters,
                "disallowed_pairs": disallowed_pairs
            },
            "ground_truth_dag": dag_gen.export_spec()
        }
