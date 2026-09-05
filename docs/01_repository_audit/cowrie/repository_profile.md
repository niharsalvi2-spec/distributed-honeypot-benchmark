# Cowrie Repository Profile
> **Repository:** `cowrie` | **Tier:** Primary | **Evidence Level:** Level 2 (Source-Code Verified)

## 1. Executive Summary
Empirical audit performed by **Team Gamergenix** (PCCOE, Pune) against cloned upstream source code.

## 2. Five-Level Evidence Evaluation
| Level | Status | Evidence Description |
| :--- | :--- | :--- |
| **Level 1: Documentation** | `CLAIMED` | Claims interactive medium/high interaction SSH/Telnet emulation. |
| **Level 2: Source Verification** | `VERIFIED` | Verified in src/cowrie/ssh/ and src/cowrie/telnet/. 520 source files. |
| **Level 3: Local Deployment** | `VERIFIED` | Configuration and runtime environment checked. |
| **Level 4: Controlled Experiment**| `SCHEDULED` | Scheduled under experiment test suite. |
| **Level 5: Measured Result** | `PENDING` | Awaiting benchmark run telemetry. |

## 3. Technical Source Findings
Cowrie provides rich terminal command capture via Twisted, but operates strictly as a single-node daemon. Log outputs in src/cowrie/output/ (38 plugins) format events independently without causal linkages.

## 4. Architectural & Research Gap Assessment
- **Cross-Service Correlation:** `UNSUPPORTED (0 source references)`
- **Logical Event Ordering:** `UNSUPPORTED (No Lamport or Vector Clocks)`
- **Timestamp Mechanism:** `Physical UTC ISO-8601 (datetime.now(timezone.utc)). No logical clocks.`
- **Session Model:** `UUID per connection generated in src/cowrie/core/session.py.`
