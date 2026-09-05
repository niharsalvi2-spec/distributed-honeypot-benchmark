# Experiment E07: Clock Perturbation & Causal Event Ordering
> **Status:** `CONFIRMED` | **Suite:** Distributed Honeypot Benchmark Framework (Team Gamergenix, PCCOE)

---

## 1. Scientific Hypothesis
- **Hypothesis $H_{\text{clock}}$:** *Logical and causal ordering mechanisms (Lamport Timestamps and Vector Clocks) will reduce sequence ordering errors under controlled clock skew and network jitter compared with uncoordinated physical timestamp ordering.*
- **Methodological Standard:** The benchmark does not assume a predetermined numerical outcome (such as "0% error"). Instead, empirical trials record observed inversion rates across varying perturbations and report actual measured data.

---

## 2. Experimental Design & Independent Variables

### Controlled Clock Skew Treatments:
The experiment injects artificial offsets across distributed nodes:
1. **Condition 1:** $0\text{ ms}$ (Baseline synchronized / no injected skew)
2. **Condition 2:** $500\text{ ms}$ simulated skew
3. **Condition 3:** $1000\text{ ms}$ ($1\text{ s}$) simulated skew
4. **Condition 4:** $2000\text{ ms}$ ($2\text{ s}$) simulated skew
5. **Condition 5:** $5000\text{ ms}$ ($5\text{ s}$) simulated skew

---

## 3. Dependent Variables & Measured Metrics

For each skew level across 10 randomized trials:
1. **Physical Timestamp Inversion Rate:** Percentage of pairwise events whose arrival order conflicts with ground-truth execution order.
2. **Lamport Ordering Error Rate:** Sequence reconstruction error using Lamport scalar clocks.
3. **Vector Clock Ordering Error Rate:** Sequence reconstruction error using multi-node Vector Clocks.
4. **Kendall's Tau ($\tau$):** Rank correlation coefficient between ground-truth sequence and reconstructed sequence.

---

## 4. Execution Protocol
```bash
python experiments/E07_clock_perturbation/runner.py --treatments "0,500,1000,2000,5000" --trials 10
```
Raw outputs are recorded immutably under `data/raw/<run_id>/` and evaluated against `data/ground_truth/`.
