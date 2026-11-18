
import csv
import statistics
from pathlib import Path
import matplotlib.pyplot as plt

folder = Path(__file__).resolve().parent

with (folder / "tp07_runs.csv").open() as f:
    rows = list(csv.DictReader(f))

metrics = [
    ("RTT_mean_ms", "RTT moyen (ms)", "RTT_vs_clients.png"),
    ("PDR_pct", "PDR applicatif (%)", "PDR_vs_clients.png"),
    ("Success_pct", "Success Rate (%)", "Success_vs_clients.png"),
]

for key, ylabel, filename in metrics:
    x = []
    means = []
    stds = []

    for clients in [5, 10, 20]:
        values = [
            float(r[key]) for r in rows
            if int(r["clients"]) == clients and r[key] != ""
        ]

        if not values:
            continue

        x.append(clients)
        means.append(statistics.mean(values))
        stds.append(
            statistics.stdev(values)
            if len(values) > 1 else 0
        )

    if not x:
        continue

    plt.figure(figsize=(8, 5))
    plt.errorbar(
        x, means, yerr=stds,
        fmt="o-", capsize=5
    )

    plt.xticks(x)
    plt.xlabel("Nombre de capteurs CoAP")
    plt.ylabel(ylabel)
    plt.title(ylabel + " selon le nombre de capteurs")
    plt.grid(alpha=0.25)
    plt.tight_layout()

    plt.savefig(folder / filename, dpi=200)
    plt.close()

    print("Created:", filename)
