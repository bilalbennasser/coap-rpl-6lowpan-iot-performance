from pathlib import Path
from statistics import mean, stdev
import csv
import re

import argparse

parser = argparse.ArgumentParser(
    description="TP08 preliminary analysis (Q1 and Q2 only)"
)
parser.add_argument("--logs-dir", type=Path, required=True)
parser.add_argument("--output-dir", type=Path, required=True)
args = parser.parse_args()

logs_dir = args.logs_dir.expanduser().resolve()
out = args.output_dir.expanduser().resolve()

if not logs_dir.is_dir():
    parser.error(f"Logs directory not found: {logs_dir}")

out.mkdir(parents=True, exist_ok=True)
seeds = (12345, 23456, 34567)
rows = []

kind_re = re.compile(r"\bTEMP_(TX|RX|ACK|TIMEOUT)\b")
id_re = re.compile(r"\bid=(\d+)")
seq_re = re.compile(r"\bseq=(\d+)")
rtt_re = re.compile(r"\brtt_ms=(\d+)")

for mode in ("CON", "NON"):
    for quality in ("Q1", "Q2"):
        for seed in seeds:
            name = f"TP08_{mode}_{quality}_seed{seed}"
            path = logs_dir / f"{name}.log"

            if not path.is_file():
                raise SystemExit(f"LOG MANQUANT: {path}")

            events = {k: set() for k in
                      ("TX", "RX", "ACK", "TIMEOUT")}
            rx_total = 0
            rtts = {}

            for line in path.read_text(errors="replace").splitlines():
                event = kind_re.search(line)
                node = id_re.search(line)
                seq = seq_re.search(line)

                if not (event and node and seq):
                    continue

                kind = event.group(1)
                key = (int(node.group(1)), int(seq.group(1)))
                events[kind].add(key)

                if kind == "RX":
                    rx_total += 1

                if kind == "ACK":
                    rtt = rtt_re.search(line)
                    if rtt:
                        rtts[key] = int(rtt.group(1))

            tx = events["TX"]
            rx = events["RX"]
            ack = events["ACK"]

            if not tx:
                raise SystemExit(f"AUCUN TEMP_TX: {name}")

            delivered = len(tx & rx)
            acknowledged = len(tx & ack)
            matched_rtts = [v for k, v in rtts.items() if k in tx]

            row = {
                "Mode": mode,
                "Qualite": quality,
                "Seed": seed,
                "TX": len(tx),
                "RX": delivered,
                "PDR_pct": round(100 * delivered / len(tx), 3),
                "RX_duplicates": rx_total - len(rx),
                "ACK": acknowledged if mode == "CON" else "NA",
                "Reponses_pct": round(
                    100 * acknowledged / len(tx), 3
                ) if mode == "CON" else "NA",
                "Timeouts": len(events["TIMEOUT"]),
                "RTT_moy_ms": round(mean(matched_rtts), 2)
                if matched_rtts else "NA"
            }

            rows.append(row)

with (out / "tp08_runs.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=rows[0].keys())
    writer.writeheader()
    writer.writerows(rows)

print("\n===== RESULTATS TP08 =====")
print("Mode  Qual  TX  RX   PDR    ACK    RTT moyen")

for row in rows:
    print(
        f"{row['Mode']:4}  {row['Qualite']:3}  "
        f"{row['TX']:3}  {row['RX']:3}  "
        f"{row['PDR_pct']:5.1f}%  "
        f"{str(row['ACK']):>4}   "
        f"{row['RTT_moy_ms']}"
    )

groups = []
print("\n===== MOYENNES DES 3 SEEDS =====")

for mode in ("CON", "NON"):
    for quality in ("Q1", "Q2"):
        subset = [
            r for r in rows
            if r["Mode"] == mode and r["Qualite"] == quality
        ]
        pdrs = [r["PDR_pct"] for r in subset]
        rtt_values = [
            r["RTT_moy_ms"] for r in subset
            if isinstance(r["RTT_moy_ms"], (int, float))
        ]

        group = {
            "Mode": mode,
            "Qualite": quality,
            "PDR_moyen_pct": round(mean(pdrs), 3),
            "PDR_ecart_type": round(stdev(pdrs), 3),
            "RTT_moy_ms": round(mean(rtt_values), 2)
            if rtt_values else "NA"
        }
        groups.append(group)
        print(group)

with (out / "tp08_summary.csv").open("w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=groups[0].keys())
    writer.writeheader()
    writer.writerows(groups)

try:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = [
        f"{g['Mode']} {g['Qualite']}" for g in groups
    ]
    values = [g["PDR_moyen_pct"] for g in groups]

    plt.figure(figsize=(9, 5))
    plt.bar(labels, values)
    plt.ylim(0, 110)
    plt.ylabel("PDR applicatif (%)")
    plt.title("TP08 - Fiabilite CoAP CON vs NON")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(out / "TP08_PDR_CON_NON.png", dpi=180)
    plt.close()

    con = [g for g in groups if g["Mode"] == "CON"]
    plt.figure(figsize=(7, 5))
    plt.bar(
        [g["Qualite"] for g in con],
        [g["RTT_moy_ms"] for g in con]
    )
    plt.ylabel("RTT moyen (ms)")
    plt.title("TP08 - RTT CoAP CON : Q1 vs Q2")
    plt.grid(axis="y", alpha=0.25)
    plt.tight_layout()
    plt.savefig(out / "TP08_RTT_CON.png", dpi=180)
    plt.close()

    print("\nGRAPHIQUES CREES : 2")

except ImportError:
    print("\nMatplotlib absent : CSV crees, graphiques non crees.")

print("\nANALYSE TERMINEE")
