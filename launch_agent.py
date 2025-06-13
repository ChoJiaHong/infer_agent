import subprocess
import time
import signal
import sys
import math
import random

# 系統參數
SERVER_FPS = 200
BATCH_SIZE = 5
AGENT_COUNT = 10
USE_SLOT_SCHEDULING = True
NUM_SLOTS = int(AGENT_COUNT/BATCH_SIZE)

# 計算每個 agent 的頻率
FREQ = int(SERVER_FPS / AGENT_COUNT)
if FREQ <= 0:
    raise ValueError("FREQ must be greater than 0")

T = 1.0 / FREQ
SLOT_PERIOD = T / NUM_SLOTS if NUM_SLOTS > 0 else 0
  # 對齊整秒 + 啟動緩衝

processes = []

try:
    for i in range(AGENT_COUNT):
        if USE_SLOT_SCHEDULING:
            slot_index = i % NUM_SLOTS
        else:
            slot_index = 0  # 若不排程，仍需填值

        p = subprocess.Popen([
            "python3", "agent_client.py",
            str(i),
            str(slot_index),
            str(FREQ),
        ])
        processes.append(p)

        print(f"Launched Agent {i} (Slot {slot_index}) | Freq: {FREQ:.2f}")
        time.sleep(0.2)

    print("All agents launched. Press Ctrl+C to terminate.")
    for p in processes:
        p.wait()

except KeyboardInterrupt:
    print("\nStopping all agents...")
    for p in processes:
        try:
            p.terminate()
        except Exception:
            pass
    time.sleep(1.0)
    for p in processes:
        if p.poll() is None:
            p.kill()
    sys.exit(0)
