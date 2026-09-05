# Contributing Guidelines

Thank you for contributing to the Distributed Honeypot Benchmark Framework.

### Code of Conduct & Academic Rigor
1. **Scientific Honesty:** Do not assume or fabricate capability gaps. Every capability or limitation must be verified experimentally with logs or source references.
2. **Reproducibility:** All experiment parameters, seeds, randomizations, and environment configurations must be explicitly defined in YAML files under `configs/`.
3. **Safety:** All network experiments must remain strictly within isolated Docker bridge networks (`attacker-network`, `sensor-network`). Never point benchmark workloads at public networks.

### Development Workflow
1. Fork and branch from `main`: `git checkout -b feature/experiment-e0X`
2. Follow PEP-8 guidelines, formatted with `black` and checked with `flake8`.
3. Add unit tests under `tests/unit/` and ensure full pass with `pytest`.
4. Submit PR with detailed test logs and environment specifications.
