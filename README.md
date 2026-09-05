# Distributed Honeypot Benchmark Framework
## Empirical Baseline Evaluation for Cross-Service Attacker Behaviour Correlation

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Docker](https://img.shields.io/badge/docker-compose-2496ED.svg)](docker-compose.yml)
[![Status](https://img.shields.io/badge/benchmark-experimental-orange.svg)](docs/README.md)

### Overview
This repository implements an empirical, reproducible benchmarking suite to rigorously evaluate contemporary open-source honeypots as baselines for **distributed attack event collection, logical event ordering, cross-service correlation, and multi-stage attacker sequence reconstruction**.

Developed by **Team Gamergenix** (Pimpri Chinchwad College of Engineering, Pune) as part of the Distributed Systems Mini Project research program.

### Evaluated Baselines
- **Cowrie** (Medium/High interaction SSH/Telnet decoy)
- **OpenCanary** (Modular multi-service daemon: SSH, FTP, HTTP, SMB)
- **T-Pot** (Multi-sensor Dockerized honeypot platform)
- **Dionaea** (Low/Medium interaction malware-capture honeypot)
- **Modern Honey Network (MHN)** (Centralized sensor management and collection)
- **Conpot & Honeytrap** (Secondary protocol emulators)

### Core Scientific Questions
1. **RQ1 (Distributed Observation):** Can distributed heterogeneous honeypots capture complementary attacker behaviour that is not observable from an individual isolated service?
2. **RQ2 (Cross-Node Correlation):** Can cross-node event correlation accurately reconstruct multi-service attack sequences belonging to the same attacker?
3. **RQ3 (Logical Event Ordering):** Does logical event ordering (Lamport/vector clocks) improve reconstruction accuracy over physical timestamps under clock skew and network jitter?
4. **RQ4 (Scalability):** How do throughput, latency, and correlation accuracy scale as the number of honeypot nodes increases from 1 to 10?

### Repository Navigation
```
├── docs/                 # Architectural specifications, literature audit & methodology
├── repositories/         # Cloned baseline source code, patches, and configurations
├── infrastructure/       # Docker Compose manifests, networks, fault injection scripts
├── configs/              # Benchmark, workload, and experiment configurations
├── workloads/            # Synthetic and controlled multi-stage attack campaigns
├── collectors/           # Ingestion daemons, parsers, and canonical event normalizers
├── distributed/          # Lamport & Vector Clocks, node management, ordering engines
├── correlation/          # Baseline, cross-service, cross-node, and graph correlation
├── sequence_reconstruction/ # Attack graph builders, causal order, attacker profiles
├── experiments/          # Automated execution harnesses for experiments E01–E10
├── data/                 # Raw logs, normalized events, and ground-truth manifests
├── analysis/             # Statistical analysis, precision/recall, and latency evaluation
├── results/              # CSV/XLSX benchmark matrices and final capability reports
├── visualizations/       # Performance curves, attack graphs, and architecture diagrams
├── benchmark/            # Core Python benchmarking framework library
├── scripts/              # Shell automation for setup, deployment, runs, and collection
├── tests/                # Unit, integration, and ground-truth validation tests
├── benchmark_specs/      # Official baseline registry and metric dictionaries (.xlsx)
├── artifacts/            # Environment snapshots, hashes, and repository metadata
└── security/             # Lab isolation policies and experiment safety protocols
```

### Quick Start
```bash
# 1. Clone dependencies and setup virtualenv
make setup

# 2. Deploy isolated single-node baseline testbed
make deploy-single

# 3. Execute functional validation experiment (E01)
python experiments/E01_functional/runner.py --config configs/experiments/E01.yaml

# 4. Run automated test suite
pytest tests/
```

For complete instructions, refer to [docs/README.md](docs/README.md) and [docs/02_benchmark_methodology/benchmark_methodology.md](docs/02_benchmark_methodology/benchmark_methodology.md).
