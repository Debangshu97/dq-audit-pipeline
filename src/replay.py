import subprocess, sys
from datetime import date, timedelta

start, end = date(2018, 7, 23), date(2018, 8, 21)
d = start
while d <= end:
    ds = d.isoformat()
    subprocess.run([sys.executable, "src/load_batch.py", ds], check=True)
    subprocess.run([sys.executable, "src/run_checks.py", ds], check=True)
    d += timedelta(days=1)
