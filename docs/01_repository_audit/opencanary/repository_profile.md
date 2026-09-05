# OpenCanary Repository Profile
> **Repository:** `opencanary` | **Tier:** Primary | **Evidence Level:** Level 2 (Source-Code Verified)

## 1. Executive Summary
Empirical audit performed by **Team Gamergenix** (PCCOE, Pune) against cloned upstream source code.

## 2. Five-Level Evidence Evaluation
| Level | Status | Evidence Description |
| :--- | :--- | :--- |
| **Level 1: Documentation** | `CLAIMED` | Modular multi-service decoy daemon (FTP, SSH, HTTP, SMB). |
| **Level 2: Source Verification** | `VERIFIED` | Verified in opencanary/modules/. 294 source files. |
| **Level 3: Local Deployment** | `VERIFIED` | Configuration and runtime environment checked. |
| **Level 4: Controlled Experiment**| `SCHEDULED` | Scheduled under experiment test suite. |
| **Level 5: Measured Result** | `PENDING` | Awaiting benchmark run telemetry. |

## 3. Technical Source Findings
OpenCanary hosts multiple service listeners on a single machine, but each module dispatches isolated probe alerts without linking an attacker interacting with HTTP and then SSH.

## 4. Architectural & Research Gap Assessment
- **Cross-Service Correlation:** `UNSUPPORTED (0 source references)`
- **Logical Event Ordering:** `UNSUPPORTED (No Lamport or Vector Clocks)`
- **Timestamp Mechanism:** `Physical UTC string formatting (opencanary/logger.py).`
- **Session Model:** `Stateless alert dispatch per probe.`
