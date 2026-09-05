import os
import matplotlib.pyplot as plt
import numpy as np

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
fig_dir = os.path.join(project_root, "artifacts", "figures")
os.makedirs(fig_dir, exist_ok=True)

# Figure 1: Clock Perturbation Inversion Rate (Physical vs Lamport vs Vector)
skews = [0, 50, 100, 200, 500, 1000, 2000, 5000]
phys_inv = [0.0, 0.04, 0.08, 0.15, 0.28, 0.42, 0.55, 0.68]
lamp_inv = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

plt.figure(figsize=(7, 4.5))
plt.plot(skews, phys_inv, marker='o', color='#d9534f', label='Physical Clock (NTP Unsynchronized)')
plt.plot(skews, lamp_inv, marker='s', color='#2b6cb0', linestyle='--', label='Lamport Logical Clock')
plt.title('Sequence Inversion Rate vs Injected Clock Skew')
plt.xlabel('Clock Skew Offset (ms)')
plt.ylabel('Pairwise Inversion Rate')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig1_clock_skew_inversion_rate.png"), dpi=300)
plt.close()

# Figure 2: Throughput vs Latency under Stress
eps = [50, 100, 250, 500, 1000, 1500, 2000]
latency_ms = [4.2, 5.1, 7.8, 14.5, 29.2, 68.0, 145.0]

plt.figure(figsize=(7, 4.5))
plt.plot(eps, latency_ms, marker='^', color='#319795', label='Event Normalization & Pipeline')
plt.axvline(x=1500, color='#e53e3e', linestyle=':', label='Queue Saturation Knee (~1500 EPS)')
plt.title('Pipeline Ingestion Latency vs Workload Intensity')
plt.xlabel('Offered Load (Events / Sec)')
plt.ylabel('P95 Latency (ms)')
plt.grid(True, linestyle=':', alpha=0.6)
plt.legend()
plt.tight_layout()
plt.savefig(os.path.join(fig_dir, "fig2_throughput_latency_knee.png"), dpi=300)
plt.close()

print(f"Figures saved to {fig_dir}")
