
import subprocess
import time

AGENT_COUNT = 8
START_DELAY = 0.5  # 每個 Agent 啟動間隔秒數


processes = []
next_agent_id = 0


def launch_agent():
    global next_agent_id
    print(f"Launching Agent #{next_agent_id}")
    p = subprocess.Popen(["python3", "agent_client.py", str(next_agent_id)])
    processes.append(p)
    next_agent_id += 1
    time.sleep(START_DELAY)


def add_agents(n: int):
    for _ in range(n):
        launch_agent()


def remove_agents(n: int):
    for _ in range(min(n, len(processes))):
        p = processes.pop()
        print("Terminating Agent")
        p.terminate()
        time.sleep(START_DELAY)


def set_agents(n: int):
    diff = n - len(processes)
    if diff > 0:
        add_agents(diff)
    elif diff < 0:
        remove_agents(-diff)


def stop_all():
    remove_agents(len(processes))


def command_loop():
    print(
        "Commands: +N to add N agents, -N to remove N agents, set N to set total,"
    )
    print("Type 'q' or 'quit' to exit.")
    while True:
        try:
            cmd = input("Command> ").strip()
        except EOFError:
            break

        if cmd in {"q", "quit", "exit"}:
            break
        elif cmd.startswith("+"):
            try:
                n = int(cmd[1:])
                add_agents(n)
            except ValueError:
                print("Invalid command")
        elif cmd.startswith("-"):
            try:
                n = int(cmd[1:])
                remove_agents(n)
            except ValueError:
                print("Invalid command")
        elif cmd.startswith("set"):
            parts = cmd.split()
            if len(parts) == 2 and parts[1].isdigit():
                set_agents(int(parts[1]))
            else:
                print("Invalid command")
        else:
            print("Unknown command")

    print("Stopping all agents...")
    stop_all()


if __name__ == "__main__":
    try:
        add_agents(AGENT_COUNT)
        command_loop()
    except KeyboardInterrupt:
        print("\nInterrupted. Stopping all agents...")
        stop_all()
