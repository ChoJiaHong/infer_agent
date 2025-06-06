import os
import re
import matplotlib.pyplot as plt

log_dir = "logs"
latency_pattern = re.compile(r"Response Latency: (?P<latency>\d+\.\d+) ms")
fps_pattern = re.compile(r"FPS - Send: (?P<send>\d+), Result: (?P<result>\d+)")

agent_data = {}

for filename in os.listdir(log_dir):
    if not filename.startswith("agent_") or not filename.endswith(".log"):
        continue

    agent_id = filename.split("_")[1].split(".")[0]
    file_path = os.path.join(log_dir, filename)

    latencies = []
    fps_send = []
    fps_result = []

    with open(file_path, "r") as f:
        for line in f:
            latency_match = latency_pattern.search(line)
            fps_match = fps_pattern.search(line)

            if latency_match:
                latencies.append(float(latency_match.group("latency")))

            if fps_match:
                fps_send.append(int(fps_match.group("send")))
                fps_result.append(int(fps_match.group("result")))

    agent_data[agent_id] = {
        "latencies": latencies,
        "fps_send": fps_send,
        "fps_result": fps_result,
    }

# Plotting
for agent_id, data in agent_data.items():
    if data["latencies"]:
        plt.figure()
        plt.plot(range(len(data["latencies"])), data["latencies"])
        plt.title(f"Agent {agent_id} - Response Latency (ms)")
        plt.xlabel("Request Count")
        plt.ylabel("Latency (ms)")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"logs/agent_{agent_id}_latency.png")
        plt.close()

    if data["fps_send"]:
        plt.figure()
        plt.plot(range(len(data["fps_send"])), data["fps_send"], label="Send FPS")
        plt.plot(range(len(data["fps_result"])), data["fps_result"], label="Result FPS")
        plt.title(f"Agent {agent_id} - FPS Trend")
        plt.xlabel("Time Tick (s)")
        plt.ylabel("FPS")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.savefig(f"logs/agent_{agent_id}_fps.png")
        plt.close()

print("Log analysis complete. Plots saved to 'logs/' folder.")
