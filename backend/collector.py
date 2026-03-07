from kubernetes import client, config
import pandas as pd
import time
import os
import random

FILE_PATH = "data/storage.csv"
TOTAL_STORAGE = 10

config.load_kube_config(config_file="/etc/rancher/k3s/k3s.yaml")
v1 = client.CoreV1Api()


def get_last_storage(pod):

    if not os.path.exists(FILE_PATH):
        return 0.1

    df = pd.read_csv(FILE_PATH)

    pod_rows = df[df["pod"] == pod]

    if len(pod_rows) == 0:
        return 0.1

    return pod_rows.iloc[-1]["storage_used"]


def collect_data():

    pods = v1.list_pod_for_all_namespaces(watch=False)

    records = []

    for pod in pods.items:

        namespace = pod.metadata.namespace

        if namespace != "default":
            continue

        pod_name = pod.metadata.name

        last_storage = get_last_storage(pod_name)

        growth = 0

        if "redis" in pod_name:
            growth = random.uniform(0.3, 0.8)

        elif "mongodb" in pod_name:
            growth = random.uniform(0.02, 0.05)

        new_storage = min(last_storage + growth, TOTAL_STORAGE)

        record = {
            "timestamp": time.time(),
            "pod": pod_name,
            "namespace": namespace,
            "status": pod.status.phase,
            "node": pod.spec.node_name,
            "storage_used": new_storage,
            "total_storage": TOTAL_STORAGE
        }

        records.append(record)

    if not records:
        return

    os.makedirs("data", exist_ok=True)

    df = pd.DataFrame(records)

    if not os.path.exists(FILE_PATH):
        df.to_csv(FILE_PATH, index=False)
    else:
        df.to_csv(FILE_PATH, mode="a", header=False, index=False)

    print("Collected:", records)