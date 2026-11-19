
import csv
import re
import statistics
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Analyze TP07 CoAP scalability experiments"
)
parser.add_argument(
    "--logs-dir", type=Path, required=True
)
parser.add_argument(
    "--output-dir", type=Path, required=True
)
args = parser.parse_args()

logs_dir = args.logs_dir.expanduser().resolve()
output_dir = args.output_dir.expanduser().resolve()

if not logs_dir.is_dir():
    parser.error(f"Logs directory not found: {logs_dir}")

output_dir.mkdir(parents=True, exist_ok=True)

pattern = re.compile(
    r"\bTEMP_(TX|RX|ACK|TIMEOUT|ERROR)"
    r"\s+id=(\d+)[,\s]+seq=(\d+)\b"
)

runs = []
per_node = []

for file in sorted(logs_dir.glob("S[123]_seed*.log")):
    name = re.fullmatch(r"S([123])_seed(\d+)", file.stem)

    if not name:
        continue

    scenario = int(name.group(1))
    seed = int(name.group(2))
    clients = {1: 5, 2: 10, 3: 20}[scenario]

    tx = set()
    rx = set()
    acks = {}
    timeouts = set()
    errors = set()

    for line in file.open(errors="replace"):
        m = pattern.search(line)

        if not m:
            continue

        kind = m.group(1)
        node = int(m.group(2))
        seq = int(m.group(3))
        key = (node, seq)

        if kind == "TX":
            tx.add(key)
        elif kind == "RX":
            rx.add(key)
        elif kind == "ACK":
            rtt = re.search(r"\brtt_ms=(\d+)\b", line)
            if rtt:
                acks[key] = int(rtt.group(1))
        elif kind == "TIMEOUT":
            timeouts.add(key)
        elif kind == "ERROR":
            errors.add(key)

    def metrics(node_id=None):
        selected = {
            k for k in tx
            if node_id is None or k[0] == node_id
        }

        count = len(selected)
        delivered = len(selected & rx)
        successful = selected & acks.keys()
        rtts = [acks[k] for k in successful]

        pending = selected - (
            acks.keys() | timeouts | errors
        )

        return {
            "TX": count,
            "RX": delivered,
            "ACK": len(successful),
            "Timeouts": len(selected & timeouts),
            "Pending": len(pending),
            "PDR_pct": round(
                100 * delivered / count, 3
            ) if count else "",
            "Success_pct": round(
                100 * len(successful) / count, 3
            ) if count else "",
            "RTT_mean_ms": round(
                statistics.mean(rtts), 2
            ) if rtts else ""
        }

    common = {
        "scenario": f"S{scenario}",
        "seed": seed,
        "clients": clients
    }

    runs.append({**common, **metrics()})

    for node in range(2, clients + 2):
        per_node.append({
            **common,
            "node": node,
            **metrics(node)
        })

    missing = [
        n for n in range(2, clients + 2)
        if not any(k[0] == n for k in tx)
    ]

    inconsistencies = len((acks.keys() & tx) - rx)

    print(f"\n{file.name}")
    print(metrics())

    if missing or inconsistencies or (rx - tx):
        print(
            "ATTENTION:",
            "missing nodes =", missing,
            "ACK without RX =", inconsistencies,
            "RX without TX =", len(rx - tx)
        )

for filename, rows in [
    ("tp07_runs.csv", runs),
    ("tp07_per_node.csv", per_node)
]:
    if rows:
        with (output_dir / filename).open(
            "w", newline=""
        ) as f:
            writer = csv.DictWriter(
                f, fieldnames=list(rows[0])
            )
            writer.writeheader()
            writer.writerows(rows)

if not runs:
    print("Aucun fichier de log trouve.")
else:
    print("\nAnalyse terminee.")
    print("Nombre de simulations analysees:", len(runs))
    print("CSV generes: tp07_runs.csv, tp07_per_node.csv")
