# T-Pot Repository Profile
> **Repository:** `tpot` | **Tier:** Primary | **Evidence Level:** Level 2 (Source-Code Verified)

## 1. Executive Summary
Empirical audit performed by **Team Gamergenix** (PCCOE, Pune) against cloned upstream source code.

## 2. Five-Level Evidence Evaluation
| Level | Status | Evidence Description |
| :--- | :--- | :--- |
| **Level 1: Documentation** | `CLAIMED` | Multi-honeypot platform running 20+ honeypots via Docker. |
| **Level 2: Source Verification** | `VERIFIED` | Verified in compose files and installer scripts. 2,275 source files. |
| **Level 3: Local Deployment** | `VERIFIED` | Configuration and runtime environment checked. |
| **Level 4: Controlled Experiment**| `SCHEDULED` | Scheduled under experiment test suite. |
| **Level 5: Measured Result** | `PENDING` | Awaiting benchmark run telemetry. |

## 3. Technical Source Findings
T-Pot unifies visualization into Kibana dashboards, but Elasticsearch indexing is purely time-series/IP matching. No causal event ordering or graph reconstruction.

## 4. Architectural & Research Gap Assessment
- **Cross-Service Correlation:** `UNSUPPORTED (0 source references)`
- **Logical Event Ordering:** `UNSUPPORTED (No Lamport or Vector Clocks)`
- **Timestamp Mechanism:** `Physical timestamps indexed by Logstash into Elasticsearch.`
- **Session Model:** `Delegated to individual underlying honeypots.`
