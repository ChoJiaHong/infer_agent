import os
import re
import matplotlib.pyplot as plt

log_dir = "logs"
drift_pattern = re.compile(r"Slot Drift: ([\-\d\.]+) ms")
latency_pattern = re.compile(r"Latency: ([\d\.]+) ms")

for filename in os.listdir(log_dir):
    if not filename.endswith("_timestamp.log"):
        continue

    agent_id = filename.split("_")[1]
    filepath = os.path.join(log_dir, filename)

    drifts = []
    latencies = []

    with open(filepath, "r") as f:
        for line in f:
            drift_match = drift_pattern.search(line)
            latency_match = latency_pattern.search(line)

            if drift_match:
                drifts.append(float(drift_match.group(1)))
            if latency_match:
                latencies.append(float(latency_match.group(1)))

    if not drifts or not latencies:
        print(f"Agent {agent_id}: insufficient data")
        continue

    # Plot Slot Drift
    plt.figure()
    plt.plot(drifts, label="Slot Drift (ms)")
    plt.axhline(y=0, linestyle='--', color='gray')
    plt.title(f"Agent {agent_id} - Slot Drift")
    plt.xlabel("Request Index")
    plt.ylabel("Drift (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"logs/agent_{agent_id}_slot_drift.png")
    plt.close()

    # Plot Latency
    plt.figure()
    plt.plot(latencies, label="Latency (ms)", color='orange')
    plt.title(f"Agent {agent_id} - Latency")
    plt.xlabel("Request Index")
    plt.ylabel("Latency (ms)")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"logs/agent_{agent_id}_latency.png")
    plt.close()

    print(f"Agent {agent_id}: Drift & Latency plots saved.")

print("Analysis complete.")
