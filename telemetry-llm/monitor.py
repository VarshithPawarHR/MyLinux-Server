
import requests
import pandas as pd
import numpy as np
from datetime import datetime
import os

PROMETHEUS = "http://localhost:9090"
CPU_QUERY = "100 - (avg by (instance) (irate(node_cpu_seconds_total{mode='idle'}[1m])) * 100)"
CSV_FILE = "cpu_data.csv"

def get_cpu_usage():
    try:
        res = requests.get(f"{PROMETHEUS}/api/v1/query", params={"query": CPU_QUERY})
        data = res.json()['data']['result']
        if not data:
            return None
        cpu = float(data[0]['value'][1])
        return cpu
    except Exception as e:
        print(f"Error querying Prometheus: {e}")
        return None

def update_csv(cpu):
    now = datetime.utcnow().isoformat()
    row = {"timestamp": now, "cpu": cpu}
    df = pd.DataFrame([row])
    if os.path.exists(CSV_FILE):
        df.to_csv(CSV_FILE, mode='a', header=False, index=False)
    else:
        df.to_csv(CSV_FILE, index=False)
    

def check_zscore(cpu):
    df = pd.read_csv(CSV_FILE)
    series = df['cpu']
    mean = np.mean(series)
    std = np.std(series)
    z = (cpu - mean) / std if std > 0 else 0
    return abs(z) > 2.0

if __name__ == "__main__":
    cpu = get_cpu_usage()
    if cpu is None:
        print("⚠️No CPU data from Prometheus.")
        exit()

    update_csv(cpu)

    if check_zscore(cpu):
        print(" ")
