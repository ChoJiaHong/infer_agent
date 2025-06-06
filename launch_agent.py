
import subprocess
import time

AGENT_COUNT = 8
START_DELAY = 0.5  # 每個 Agent 啟動間隔秒數


processes = []

for i in range(AGENT_COUNT):
    print(f"Launching Agent #{i}")
    p = subprocess.Popen(["python3", "agent_client.py", str(i)])
    processes.append(p)
    time.sleep(START_DELAY)

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    print("Stopping all agents...")
    for p in processes:
        p.terminate()
