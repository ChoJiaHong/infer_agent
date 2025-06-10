import subprocess
import time
import signal
import sys
import math
SERVER_FPS=220
AGENT_COUNT = 10
FREQ = SERVER_FPS / AGENT_COUNT  # 每個 Agent 的頻率
if FREQ <= 0:
    raise ValueError("FREQ must be greater than 0, check AGENT_COUNT and SERVER_FPS.")
USE_SLOT_SCHEDULING = True  # 設為 False 即不排程
NUM_SLOTS = 2
T = 1.0 / FREQ
SLOT_PERIOD = T / NUM_SLOTS if NUM_SLOTS > 0 else 0

# 設定公用的 base_time：向上取數到整數秒，預留1.5秒啟動延遲
BASE_TIME = math.ceil(time.time() + 5)

processes = []

try:
    for i in range(AGENT_COUNT):
        if USE_SLOT_SCHEDULING:
            slot_index = i % NUM_SLOTS
            slot_offset = slot_index * SLOT_PERIOD
        else:
            slot_offset = 0.0

        p = subprocess.Popen([
            "python3", "agent_client.py",
            str(i),
            str(slot_offset),
            str(BASE_TIME)
        ])
        processes.append(p)

        print(f"Launched Agent {i} with slot offset {slot_offset:.6f}s" +
              (f" (Slot {slot_index})" if USE_SLOT_SCHEDULING else "") +
              f" | Base time: {BASE_TIME}")
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
