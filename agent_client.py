import grpc
import time
import asyncio
import cv2
import numpy as np
import pose_pb2
import pose_pb2_grpc
import sys
import logging
import os
from datetime import datetime
import atexit
import uvloop

# 取得 agent ID 與 slot offset 與 base_time
AGENT_ID = int(sys.argv[1]) if len(sys.argv) > 1 else 0
AGENT_SLOT_OFFSET = float(sys.argv[2]) if len(sys.argv) > 2 else 0.0
AGENT_BASE_TIME = float(sys.argv[3]) if len(sys.argv) > 3 else time.time()

# 設定 log 資料
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f"agent_{AGENT_ID}_timestamp.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [Agent %(name)s] %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler(log_path),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(f"{AGENT_ID}")

@atexit.register
def log_exit():
    logger.info("Agent exiting cleanly.")

# 初始化全域變數
image_path = '1280.jpg'
SERVER_ADDRESS = '172.22.9.141:30561'
POSE_SEND_FPS = 0
POSE_RESULT_FPS = 0
POSE_TIMEOUT = 0.1
FREQ = 15.0
INTERVAL = 1.0 / FREQ

image_data = None

def encode_dummy_image():
    global image_data
    if image_data is None:
        with open(image_path, "rb") as f:
            image_data = f.read()
    return image_data

# 使用 slot-based 精準發送
async def send_pose_request(stub):
    global POSE_SEND_FPS, POSE_RESULT_FPS

    now = time.time()
    sleep_time = AGENT_BASE_TIME - now
    if sleep_time > 0:
        logger.info(f"Waiting {sleep_time:.3f}s for base time alignment...")
        await asyncio.sleep(sleep_time)

    base_time = time.perf_counter()
    next_slot_time = base_time + AGENT_SLOT_OFFSET

    while True:
        now = time.perf_counter()
        drift = (now - next_slot_time) * 1000
        next_slot_time += INTERVAL

        send_ts = datetime.utcnow().isoformat(timespec='microseconds')
        request = pose_pb2.FrameRequest(image_data=encode_dummy_image())
        POSE_SEND_FPS += 1

        try:
            t1 = time.perf_counter()
            response = await stub.SkeletonFrame(request, timeout=POSE_TIMEOUT)
            t2 = time.perf_counter()
            recv_ts = datetime.utcnow().isoformat(timespec='microseconds')
            latency = (t2 - t1) * 1000
            logger.info(f"Slot Drift: {drift:.3f} ms | Send Time: {send_ts}, Receive Time: {recv_ts}, Latency: {latency:.2f} ms")
            POSE_RESULT_FPS += 1
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC Error: {e.code()} - {e.details()}")

        remaining = next_slot_time - time.perf_counter()
        if remaining > 0:
            await asyncio.sleep(remaining)

# 統計 FPS
async def monitor_fps():
    global POSE_SEND_FPS, POSE_RESULT_FPS
    while True:
        logger.info(f"FPS - Send: {POSE_SEND_FPS}, Result: {POSE_RESULT_FPS}")
        POSE_SEND_FPS = 0
        POSE_RESULT_FPS = 0
        await asyncio.sleep(1)

async def main():
    logger.info(f"Connecting to gRPC server at {SERVER_ADDRESS}")
    async with grpc.aio.insecure_channel(SERVER_ADDRESS) as channel:
        stub = pose_pb2_grpc.MirrorStub(channel)
        await asyncio.gather(
            monitor_fps(),
            send_pose_request(stub),
        )

if __name__ == "__main__":
    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
    asyncio.run(main())
