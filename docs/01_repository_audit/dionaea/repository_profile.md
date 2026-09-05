# Dionaea Repository Profile
> **Repository:** `dionaea` | **Tier:** Primary | **Evidence Level:** Level 2 (Source-Code Verified)

## 1. Executive Summary
Empirical audit performed by **Team Gamergenix** (PCCOE, Pune) against cloned upstream source code.

## 2. Five-Level Evidence Evaluation
| Level | Status | Evidence Description |
| :--- | :--- | :--- |
| **Level 1: Documentation** | `CLAIMED` | Malware capture honeypot emulating SMB, HTTP, FTP, TFTP. |
| **Level 2: Source Verification** | `VERIFIED` | Verified in C core and Python modules. 350 files. |
| **Level 3: Local Deployment** | `VERIFIED` | Configuration and runtime environment checked. |
| **Level 4: Controlled Experiment**| `SCHEDULED` | Scheduled under experiment test suite. |
| **Level 5: Measured Result** | `PENDING` | Awaiting benchmark run telemetry. |

## 3. Technical Source Findings
Excellent shellcode and payload capture, but strictly isolated to individual attack sessions.

## 4. Architectural & Research Gap Assessment
- **Cross-Service Correlation:** `UNSUPPORTED (0 source references)`
- **Logical Event Ordering:** `UNSUPPORTED (No Lamport or Vector Clocks)`
- **Timestamp Mechanism:** `Local system clock timestamps.`
- **Session Model:** `Connection state tracking per connection.`
