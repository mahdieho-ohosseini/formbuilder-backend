from pathlib import Path
import os

current = Path(__file__).resolve()
print("\n[1] Current file:", current)

# مسیر config.py
config_file = Path("services/iam_service/app/core/config.py").resolve()
print("\n[2] config.py:", config_file)

# نمایش parents برای محاسبه
print("\n[3] Parents of config.py:")
for i in range(6):
    print(f"parents[{i}]:", config_file.parents[i])

# تست جایگذاری env
for i in range(6):
    env_path = config_file.parents[i] / ".env"
    print(f"\n[4] Checking parents[{i}] -> {env_path}")
    print("Exists:", env_path.exists())

print("\nDone.")
