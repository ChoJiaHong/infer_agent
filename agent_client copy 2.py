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

# 取得 agent ID
AGENT_ID = sys.argv[1] if len(sys.argv) > 1 else "0"

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
logger = logging.getLogger(AGENT_ID)

# 初始化全域變數
image_path = '1280.jpg'  # 替換為你的圖片路徑
SERVER_ADDRESS = '172.22.9.141:30561'
POSE_SEND_FPS = 0
POSE_RESULT_FPS = 0
POSE_TIMEOUT = 0.1
FREQ = 15.0  # 每秒送出次數（可調整）

# 預先轉成固定圖片資料
image_data = None

def encode_dummy_image():
    global image_data
    if image_data is None:
        with open(image_path, "rb") as f:
            image_data = f.read()
    return image_data

# 傳送請求至 gRPC Server
async def send_pose_request(stub):
    global POSE_SEND_FPS, POSE_RESULT_FPS

    while True:
        start_time = time.time()
        send_timestamp = datetime.utcnow().isoformat(timespec='microseconds')
        request = pose_pb2.FrameRequest(image_data=encode_dummy_image())
        POSE_SEND_FPS += 1

        try:
            t1 = time.time()
            response = await stub.SkeletonFrame(request, timeout=POSE_TIMEOUT)
            recv_timestamp = datetime.utcnow().isoformat(timespec='microseconds')
            latency = time.time() - t1
            logger.info(f"Send Time: {send_timestamp}, Receive Time: {recv_timestamp}, Latency: {latency * 1000:.2f} ms")
            POSE_RESULT_FPS += 1
        except grpc.aio.AioRpcError as e:
            logger.error(f"gRPC Error: {e}")

        elapsed = time.time() - start_time
        sleep_time = max(0, 1 / FREQ - elapsed)
        await asyncio.sleep(sleep_time)

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
    asyncio.run(main())