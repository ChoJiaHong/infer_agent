import os
import re
import matplotlib.pyplot as plt
from datetime import datetime

log_dir = "logs"
send_time_pattern = re.compile(r"Send Time: ([\d\-T:\.]+)")

agent_timeline = {}

for filename in os.listdir(log_dir):
    if not filename.endswith("_timestamp.log"):
        continue

    agent_id = filename.split("_")[1]
    filepath = os.path.join(log_dir, filename)

    timestamps = []

    with open(filepath, "r") as f:
        for line in f:
            match = send_time_pattern.search(line)
            if match:
                ts = datetime.fromisoformat(match.group(1))
                timestamps.append(ts)

    if timestamps:
        agent_timeline[agent_id] = timestamps

# 找出最早的時間作為基準
min_time = min(ts[0] for ts in agent_timeline.values())

# 畫圖
plt.figure()
for agent_id, ts_list in agent_timeline.items():
    rel_times = [(t - min_time).total_seconds() for t in ts_list]
    y = [int(agent_id)] * len(rel_times)
    plt.scatter(rel_times, y, s=10, label=f"Agent {agent_id}")

plt.xlabel("Time since start (s)")
plt.ylabel("Agent ID")
plt.title("Agent Request Timeline")
plt.grid(True)
plt.tight_layout()
plt.savefig("logs/agent_request_timeline.png")
plt.close()

print("Timeline plot saved to logs/agent_request_timeline.png")
