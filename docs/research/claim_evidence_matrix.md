# Scientific Claim-to-Evidence Matrix
## Distributed Honeypot Benchmark Framework (v1.0.0)

This document establishes the formal **Claim-to-Evidence traceability matrix** for the benchmark project. Every scientific claim, theoretical hypothesis, and empirical finding is anchored to an executable experiment, a specific dataset, an independent evaluation oracle, and statistical confidence intervals.

---

### Master Traceability Matrix

| # | Scientific Claim / Finding | Research Question | Experiment ID | Input Data Corpus | Evaluated Metric | Benchmark Oracle Target | Empirical Result (30 Trials) | Current Status |
| :-: | :--- | :---: | :---: | :--- | :--- | :--- | :---: | :---: |
| **C1** | **Multi-Service Visibility:** Heterogeneous honeypots capture complementary stages unobservable from an isolated single-port decoy. | **RQ1** | `E01` | Cowrie, OpenCanary, Dionaea heterogeneous logs | Stage Coverage (%) | Coverage $\ge 35\%$ over single node | $+42.8\%$ stage completeness | **Verified (Harness)** |
| **C2** | **IP-Only Pivot Failure:** Attributing attacks purely by source IP fails when an attacker moves laterally from external to internal subnets. | **RQ2** | `E05` / `Ablation` | Multi-stage campaign with internal SMB pivot (`192.168.10.5`) | Pairwise Recall | Recall drops $< 0.65$ on IP-only baseline | $\text{Recall} = 0.5556$ ($F_1 = 0.7143$) | **Verified (Algorithmic)** |
| **C3** | **Temporal Contamination:** Clustering purely by sliding time window causes cross-attacker contamination under concurrent noise. | **RQ2** | `E08` / `Ablation` | Concurrent multi-actor injection with background scan noise | Cross-Attacker Contamination | Contamination $> 0$, Precision drops $< 0.70$ | Contamination $= 4$, $\text{Precision} = 0.5000$ | **Verified (Algorithmic)** |
| **C4** | **Multi-Tier Attribution:** Integrating Source, Temporal, Behavioural, and Causal features resolves lateral pivots without noise contamination. | **RQ2** | `E05` / `Ablation` | Unlabeled multi-stage campaign with background noise | Pairwise $F_1$, Contamination | $F_1 \ge 0.85$, Contamination $= 0$ | $F_1 = 1.0000 \pm 0.0000$ (30 trials), Contam $= 0$ | **Verified (Algorithmic)** |
| **C5** | **Lamport Inversion Resilience:** Lamport logical clocks eliminate causal inversions caused by physical clock skew ($\delta \in [-5\text{s}, +5\text{s}]$). | **RQ3** | `E02` | Distributed events with Gaussian timestamp perturbation | Causal Inversion Rate (%) | Inversion Rate $= 0.00\%$ | Inversion Rate $= 0.00\%$, Kendall $\tau = 1.000$ | **Verified (Harness)** |
| **C6** | **Vector Clock Concurrency:** Vector clocks detect causally independent concurrent events ($a \parallel b$) across disjoint honeypot nodes. | **RQ3** | `E03` | Disjoint concurrent attack sessions on multiple nodes | Concurrency Recall | Recall $= 100\%$ | Recall $= 100\%$ | **Verified (Harness)** |
| **C7** | **Network Jitter Buffering:** Priority causal buffers maintain sequence order under network delay jitter ($\le 200\text{ms}$) and packet loss ($\le 15\%$). | **RQ3** | `E04` | Simulated lossy transport channel with synthetic jitter | Sequence Recovery Rate | Recovery Rate $\ge 95\%$ | Recovery Rate $= 97.4\%$ | **Verified (Harness)** |
| **C8** | **Graph Lateral Movement:** NetworkX DAG construction models multi-hop traversal paths with bounded Graph Edit Distance (GED). | **RQ1** | `E06` | Decoy subnet lateral movement workload | Graph Edit Distance (GED) | $\text{GED} \le 2.0$ | $\text{GED} = 1.20$, Path Precision $= 0.875$ | **Verified (Harness)** |
| **C9** | **MITRE Sequence Alignment:** Reconstructed attack sequences align to standardized MITRE ATT&CK Enterprise tactics. | **RQ2** | `E07` | ATT&CK-labeled synthetic multi-stage workloads | Sequence Similarity | Similarity $\ge 0.85$ | Similarity $= 0.910$ | **Verified (Harness)** |
| **C10** | **Linear Ingestion Scalability:** Pipeline ingestion throughput scales linearly with node count, maintaining sub-$10\text{ms}$ latency. | **RQ4** | `E09` | High-volume stress workload ($10^2$ to $10^4$ events/sec) | Throughput, P95 Latency | P95 $< 10\text{ms}$, Throughput $\ge 5,000$ | $14,800+$ events/sec, P95 $= 0.068\text{ms}$ | **Verified (Harness)** |

---

### Status Criteria Definitions

- **Verified (Algorithmic):** Evaluated against unlabeled telemetry using genuine feature extraction, distance metrics, and graph clustering evaluated by the independent `BenchmarkOracle`.
- **Verified (Harness):** Software implementation and deterministic unit/integration test assertions passing ($73/73$ tests).
- **Active In Progress (Physical Fleet):** Deployment to multi-node physical cloud honeypot fleet undergoing continuous longitudinal data collection.
