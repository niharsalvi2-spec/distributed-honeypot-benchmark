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
