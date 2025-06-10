import os
import re
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

log_dir = "logs"
send_time_pattern = re.compile(r"Send Time: ([\d\-T:\.]+)")

FREQ = 15.0  # 與 agent 發送頻率一致
T = 1.0 / FREQ
SLOT_BIN_MS = 5  # slot 對齊誤差容忍度（ms）

slot_usage = {}  # {agent_id: {slot_bin_index: count}}

for filename in os.listdir(log_dir):
    if not filename.endswith("_timestamp.log"):
        continue

    agent_id = int(filename.split("_")[1])
    filepath = os.path.join(log_dir, filename)

    with open(filepath, "r") as f:
        for line in f:
            match = send_time_pattern.search(line)
            if not match:
                continue

            send_time = datetime.fromisoformat(match.group(1))
            ts_ms = send_time.timestamp() * 1000  # 絕對毫秒時間
            bin_index = round((ts_ms % (T * 1000)) / SLOT_BIN_MS)

            if agent_id not in slot_usage:
                slot_usage[agent_id] = {}
            slot_usage[agent_id][bin_index] = slot_usage[agent_id].get(bin_index, 0) + 1

# 準備 heatmap 矩陣
max_slot = max(max(d.keys()) for d in slot_usage.values())
agent_ids = sorted(slot_usage.keys())
matrix = np.zeros((len(agent_ids), max_slot + 1))

for i, agent_id in enumerate(agent_ids):
    for slot_idx, count in slot_usage[agent_id].items():
        matrix[i, slot_idx] = count

plt.figure(figsize=(10, 6))
plt.imshow(matrix, aspect='auto', cmap='viridis')
plt.colorbar(label='Request Count')
plt.xlabel('Slot Bin Index (5ms/bin)')
plt.ylabel('Agent ID')
plt.title('Agent vs Slot Usage Heatmap')
plt.tight_layout()
plt.savefig("logs/slot_usage_heatmap.png")
plt.close()

print("Slot usage heatmap saved to logs/slot_usage_heatmap.png")
