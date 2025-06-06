import os

log_dir = "logs"

# 清除 logs 資料夾中所有 png 圖片
for filename in os.listdir(log_dir):
    if filename.endswith("_timestamp.log"):
        filepath = os.path.join(log_dir, filename)
        os.remove(filepath)
        print(f"Deleted: {filepath}")

print("All log images deleted.")
