# Benchmark Master Architecture & Data Lifecycle Policy
## Distributed Cross-Service Attacker Behaviour Correlation via Interactive Honeypots

> **Author:** Team Gamergenix, Pimpri Chinchwad College of Engineering (PCCOE), Pune  
> **Course:** Mini Project – Distributed Systems (DS)  
> **Scope:** Master Governance, Lifecycle Invariants, and Data Provenance Protocol

---

## 1. Top-Level Conceptual Architecture

```
                    DISTRIBUTED HONEYPOT
                    BENCHMARK FRAMEWORK
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   REPOSITORIES          METHODOLOGY         INFRASTRUCTURE
        │                    │                    │
        ▼                    ▼                    ▼
 Cowrie/OpenCanary      Experiments          Docker/Network
 T-Pot/Dionaea          Ground Truth         Monitoring
 MHN/etc.               Metrics              Fault Injection
        │
        ▼
    DEPLOYMENT
        │
        ▼
  CONTROLLED WORKLOAD
        │
        ▼
     RAW EVENTS
        │
        ▼
   EVENT INGESTION
        │
        ▼
      PARSING
        │
        ▼
    NORMALIZATION
        │
        ▼
 ┌──────┴─────────┐
 │                │
 ▼                ▼
TIMESTAMP      LOGICAL CLOCK
 │                │
 │          ┌─────┴─────┐
 │          ▼           ▼
 │       Lamport      Vector
 │          │           │
 └──────────┴─────┬─────┘
                  ▼
              ORDERING
                  │
                  ▼
             CORRELATION
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   Same Node  Cross-Service Cross-Node
       │          │          │
       └──────────┼──────────┘
                  ▼
            EVENT GRAPH
                  │
                  ▼
        ATTACK SEQUENCE
          RECONSTRUCTION
                  │
                  ▼
        ATTACKER BEHAVIOUR
              PROFILE
                  │
                  ▼
             EVALUATION
                  │
       ┌──────────┼──────────┐
       ▼          ▼          ▼
   Precision    Recall      F1
       │          │          │
       └──────────┼──────────┘
                  ▼
          PERFORMANCE
          SCALABILITY
          RELIABILITY
                  │
                  ▼
        STATISTICAL ANALYSIS
                  │
                  ▼
        VALIDATED RESEARCH GAP
                  │
                  ▼
          REQUIREMENTS FOR
        YOUR PROPOSED SYSTEM
```

---

## 2. The Strict Data Lifecycle & Immutability Invariant

All benchmark execution data must progress through a unidirectional, non-destructive pipeline:

```
RAW ─────────► PARSED ────────► ORDERED ─────────► CORRELATED ────────► RECONSTRUCTED ──────► EVALUATED
 │                 │               │                    │                     │                   │
 ▼                 ▼               ▼                    ▼                     ▼                   ▼
data/raw/   data/normalized/   data/processed/   data/processed/       data/processed/         results/
                                 ordering/         correlation/          sequences/
```

### Invariants:
1. **Never Overwrite Raw Telemetry:** Raw logs in `data/raw/<repository>/run_XXX/` are strictly immutable once written by the collector.
2. **Deterministic Derived Data:** Every artifact in `normalized/`, `processed/`, and `results/` is reproducible from raw data + workload manifest + configuration version.
3. **Traceable Data Lineage:** For any figure or table in the final report, complete auditability is enforced:
   $$\text{Figure} \to \text{Analysis} \to \text{Processed Dataset} \to \text{Normalized Events} \to \text{Raw Logs} \to \text{Run ID} \to \text{Commit Hash} \to \text{Config}$$

---

## 3. The 6-Phase Research Roadmap

```
Phase 1: Repository Audit (Deep dive into existing honeypots)
         ↓
Phase 2: Deployment (Docker orchestration, testbed networks, configs)
         ↓
Phase 3: Event Collection (Ingestion, multi-engine parsers, canonical normalization)
         ↓
Phase 4: Distributed Experiments (Clocks, workloads, experiments E01–E10)
         ↓
Phase 5: Research Evaluation (Correlation math, attack graphs, profiles, statistical rigor)
         ↓
Phase 6: Proposed System Implementation (Building our custom distributed correlation system)
```

The scientific principle:
$$\text{Existing Systems} \to \text{Empirical Benchmark} \to \text{Observed Limitations} \to \text{Validated Gap} \to \text{Requirements} \to \text{Our Proposed System}$$

---

## 4. Machine-Readable Source of Truth

- **Primary Source of Truth:** Machine-readable YAML/JSON configs under `configs/` (`repositories.yaml`, `metrics.yaml`, `experiments/*.yaml`).
- **Secondary Generated Reports:** Excel spreadsheets under `benchmark_specs/` and `results/final/` are compiled artifacts generated via automated scripts from the YAML definitions, ensuring programmatic CI/CD validation.
