# Cowrie Logging Architecture
> **Repository:** `cowrie` | **Tier:** Primary | **Evidence Level:** Level 2 (Source-Code Verified)

## 1. Executive Summary
Empirical audit performed by **Team Gamergenix** (PCCOE, Pune) against cloned upstream source code.

## 2. Five-Level Evidence Evaluation
| Level | Status | Evidence Description |
| :--- | :--- | :--- |
| **Level 1: Documentation** | `CLAIMED` | Supports JSON, SQLite, Elasticsearch, Syslog. |
| **Level 2: Source Verification** | `VERIFIED` | Verified in src/cowrie/output/jsonlog.py and sqlite.py. |
| **Level 3: Local Deployment** | `VERIFIED` | Configuration and runtime environment checked. |
| **Level 4: Controlled Experiment**| `SCHEDULED` | Scheduled under experiment test suite. |
| **Level 5: Measured Result** | `PENDING` | Awaiting benchmark run telemetry. |

## 3. Technical Source Findings
Outputs cowrie.json with structured events: cowrie.session.connect, cowrie.login.failed, cowrie.command.input.

## 4. Architectural & Research Gap Assessment
- **Cross-Service Correlation:** `UNSUPPORTED (0 source references)`
- **Logical Event Ordering:** `UNSUPPORTED (No Lamport or Vector Clocks)`
- **Timestamp Mechanism:** `Physical timestamps.`
- **Session Model:** `Isolated per connection`
