import subprocess
import time
import sys
import math

SERVER_FPS = 220
USE_SLOT_SCHEDULING = True  # 設為 False 即不排程
NUM_SLOTS = 2

processes = []
AGENT_COUNT = 10
FREQ = 0.0
SLOT_PERIOD = 0.0
BASE_TIME = 0.0


def calc_params(count: int):
    if count <= 0:
        raise ValueError("Agent count must be greater than 0")
    freq = SERVER_FPS / count
    if freq <= 0:
        raise ValueError("FREQ must be greater than 0, check SERVER_FPS")
    t = 1.0 / freq
    slot_period = t / NUM_SLOTS if NUM_SLOTS > 0 else 0.0
    base_time = math.ceil(time.time() + 5)
    return freq, slot_period, base_time


def propagate_params():
    """Placeholder for updating running agents with new timing parameters."""
    # TODO: Implement agent parameter update mechanism
    pass


def update_params():
    """Recalculate global timing parameters and propagate to agents."""
    global FREQ, SLOT_PERIOD, BASE_TIME
    FREQ, SLOT_PERIOD, BASE_TIME = calc_params(AGENT_COUNT)
    propagate_params()


def start_agent(index: int):
    if USE_SLOT_SCHEDULING:
        slot_index = index % NUM_SLOTS
        slot_offset = slot_index * SLOT_PERIOD
    else:
        slot_offset = 0.0

    p = subprocess.Popen([
        "python3",
        "agent_client.py",
        str(index),
        str(slot_offset),
        str(BASE_TIME),
        str(FREQ),
    ])
    processes.append(p)

    print(
        f"Launched Agent {index} with slot offset {slot_offset:.6f}s"
        + (f" (Slot {slot_index})" if USE_SLOT_SCHEDULING else "")
        + f" | Base time: {BASE_TIME} | FREQ: {FREQ}"
    )
    time.sleep(0.2)


def terminate_agent(p: subprocess.Popen):
    try:
        p.terminate()
    except Exception:
        pass
    time.sleep(1.0)
    if p.poll() is None:
        p.kill()


def stop_agents():
    for p in processes:
        terminate_agent(p)
    processes.clear()


def start_agents(count: int):
    global AGENT_COUNT
    AGENT_COUNT = count
    update_params()

    for i in range(count):
        start_agent(i)


def increase_agents(n: int):
    """Launch n additional agent processes."""
    global AGENT_COUNT
    if n <= 0:
        return
    start_index = AGENT_COUNT
    AGENT_COUNT += n
    update_params()
    for i in range(start_index, AGENT_COUNT):
        start_agent(i)


def decrease_agents(n: int):
    """Terminate n agent processes from the end of the list."""
    global AGENT_COUNT
    if n <= 0:
        return
    n = min(n, AGENT_COUNT - 1)
    for _ in range(n):
        p = processes.pop()
        terminate_agent(p)
    AGENT_COUNT -= n
    update_params()


def parse_command(cmd: str):
    cmd = cmd.strip()
    if not cmd:
        return
    if cmd.lower() in {"quit", "exit", "q"}:
        raise KeyboardInterrupt
    if cmd.startswith("+"):
        try:
            delta = int(cmd[1:] or "1")
        except ValueError:
            print("Invalid command.")
            return
        increase_agents(delta)
    elif cmd.startswith("-"):
        try:
            delta = int(cmd[1:] or "1")
        except ValueError:
            print("Invalid command.")
            return
        decrease_agents(delta)
    elif cmd.startswith("set"):
        parts = cmd.split()
        if len(parts) != 2 or not parts[1].isdigit():
            print("Usage: set N")
            return
        new_count = max(1, int(parts[1]))
        if new_count > AGENT_COUNT:
            increase_agents(new_count - AGENT_COUNT)
        elif new_count < AGENT_COUNT:
            decrease_agents(AGENT_COUNT - new_count)
        else:
            print(f"Agent count already {AGENT_COUNT}")
            return
    else:
        print("Unknown command. Use +N, -N, set N or quit.")
        return

    print(f"Running {AGENT_COUNT} agents at {FREQ:.2f} Hz each.")


def main():
    start_agents(AGENT_COUNT)
    print("Commands: +N, -N, set N, quit")
    try:
        while True:
            cmd = input("> ")
            parse_command(cmd)
    except KeyboardInterrupt:
        pass
    print("Stopping all agents...")
    stop_agents()


if __name__ == "__main__":
    main()
