import os
import re
from datetime import datetime
import matplotlib.pyplot as plt

log_dir = "logs"
send_pattern = re.compile(r"Send Time: (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d+)")

# 分析每個 agent log 的連續送出時間差距
def analyze_agent_send_intervals(agent_id):
    filepath = os.path.join(log_dir, f"agent_{agent_id}_timestamp.log")
    if not os.path.exists(filepath):
        print(f"Log file not found: {filepath}")
        return

    send_times = []
    with open(filepath, 'r') as f:
        for line in f:
            match = send_pattern.search(line)
            if match:
                ts = datetime.fromisoformat(match.group(1))
                send_times.append(ts)

    if len(send_times) < 2:
        print(f"Agent {agent_id}: Not enough send timestamps to analyze.")
        return

    intervals = [(send_times[i+1] - send_times[i]).total_seconds() * 1000 for i in range(len(send_times)-1)]
    average_interval = sum(intervals) / len(intervals)

    print(f"Agent {agent_id} - Avg Interval: {average_interval:.2f} ms, Target: {1000/20:.2f} ms, Count: {len(intervals)}")

    plt.figure()
    plt.plot(intervals, label='Interval (ms)')
    plt.axhline(y=average_interval, color='r', linestyle='--', label='Average')
    plt.axhline(y=50, color='g', linestyle=':', label='Target (50ms)')
    plt.title(f"Agent {agent_id} - Send Interval Deviation")
    plt.xlabel("Request Index")
    plt.ylabel("Interval (ms)")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"logs/agent_{agent_id}_send_interval.png")
    plt.close()

# 掃描所有 timestamp log 檔案
for agent_file in os.listdir(log_dir):
    if agent_file.endswith("_timestamp.log"):
        agent_id = agent_file.split("_")[1]
        analyze_agent_send_intervals(agent_id)

print("Send interval analysis complete. Plots saved to logs/.")
