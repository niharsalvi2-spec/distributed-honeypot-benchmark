# Benchmark Workload Profiles & Attack Schedules

This directory contains deterministic workload definitions, attack campaign timelines, fault schedules, and scalability load parameters for the Distributed Honeypot Benchmark Framework.

## Directory Structure

```
workloads/
├── benign/                         # Authorized, benign interaction sequences
│   ├── ssh/                        # Login attempts, shell maintenance commands, terminations
│   ├── http/                       # Static web requests, API exploration, crawler paths
│   └── ftp/                        # Authentication, directory listings, file downloads
│
├── controlled_attack/              # Deterministic attack campaigns with ground-truth causal links
│   ├── campaign_A/                 # Multi-stage killchain (Recon -> Exploit -> SSH -> Pivot -> Exfil)
│   ├── campaign_B/                 # Coordinated distributed botnet probe across multi-nodes
│   ├── cross_service/              # Cross-service pivoting (HTTP -> SSH -> FTP)
│   └── interleaved/                # Concurrent multi-attacker traces for separation benchmarks
│
├── fault/                          # Fault injection schedules & perturbation definitions
│   ├── clock_skew.yaml             # Asymmetric clock offsets, linear drifts, and network jitter
│   ├── node_failure.yaml           # Crash-stop and crash-recovery event injection
│   ├── network_partition.yaml     # Bipartite network isolation schedules
│   └── collector_failure.yaml      # Telemetry daemon outage and queue spooling tests
│
└── scalability/                    # Concurrency, throughput, and stress workloads
    ├── low_rate.yaml               # 50 EPS baseline
    ├── medium_rate.yaml            # 250 EPS standard load
    ├── high_rate.yaml              # 1,000 EPS saturation test
    ├── burst.yaml                  # Pulsed micro-burst traffic (3,000 EPS peak)
    └── sustained.yaml              # Continuous 500 EPS load for endurance profiling
```

## Workload Execution Principles

1. **Deterministic Ground Truth**: All attack campaigns in `controlled_attack/` define an explicit `expected_events.json` and `expected_sequence.json`. Evaluators compare observed reconstructions strictly against these causal manifests.
2. **Reproducibility**: Offsets are defined in seconds relative to experiment start ($t_0$). Random distributions (e.g. Gaussian jitter) use deterministic PRNG seeds recorded in the experiment run metadata.
3. **No Synthetic Artifacts in Raw Data**: When workloads are executed against honeypots, raw socket interactions are generated so the target honeypot logs real network events.
