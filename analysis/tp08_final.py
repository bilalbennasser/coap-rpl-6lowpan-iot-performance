from pathlib import Path
from statistics import mean, stdev
import re
import csv
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

out = Path("results/tp08")
pattern = re.compile(
    r"TEMP_(TX|RX|ACK)\s+id=(\d+)[, ]+seq=(\d+)"
)
rtt_pattern = re.compile(r"rtt_ms=(\d+)")
rows = []

for quality in ("Q1", "Q2", "Q3"):
    for mode in ("CON", "NON"):
        for seed in (12345, 23456, 34567):
            name = f"TP08_{mode}_{quality}_seed{seed}"
            path = out / f"{name}.log"

            if not path.exists():
                raise SystemExit(f"LOG MANQUANT: {path}")

            events = {k: set() for k in ("TX", "RX", "ACK")}
            rtts = {}
            rx_count = 0

            for line in path.read_text(
                errors="replace"
            ).splitlines():
                m = pattern.search(line)
                if not m:
                    continue

                kind, node, seq = m.groups()
                key = (int(node), int(seq))
                events[kind].add(key)

                if kind == "RX":
                    rx_count += 1

                if kind == "ACK":
                    rtt = rtt_pattern.search(line)
                    if rtt:
                        rtts[key] = int(rtt.group(1))

            tx = events["TX"]
            rx = tx & events["RX"]
            ack = tx & events["ACK"]

            if not tx:
                raise SystemExit(f"AUCUN TX: {name}")

            valid_rtts = [
                value for key, value in rtts.items()
                if key in tx
            ]

            rows.append({
                "Mode": mode,
                "Qualite": quality,
                "Seed": seed,
                "TX": len(tx),
                "RX": len(rx),
                "PDR_pct": 100 * len(rx) / len(tx),
                "ACK": len(ack) if mode == "CON" else "",
                "RTT_ms": mean(valid_rtts)
                if valid_rtts else ""
            })

def save_csv(filename, data):
    with (out / filename).open("w", newline="") as f:
        writer = csv.DictWriter(
            f, fieldnames=data[0].keys()
        )
        writer.writeheader()
        writer.writerows(data)

save_csv("tp08_final_runs.csv", rows)

summary = []
for quality in ("Q1", "Q2", "Q3"):
    for mode in ("CON", "NON"):
        group = [
            r for r in rows
            if r["Qualite"] == quality
            and r["Mode"] == mode
        ]
        pdrs = [r["PDR_pct"] for r in group]
        rtts = [
            r["RTT_ms"] for r in group
            if isinstance(r["RTT_ms"], (int, float))
        ]

        summary.append({
            "Mode": mode,
            "Qualite": quality,
            "PDR_moyen": round(mean(pdrs), 2),
            "PDR_ecart_type": round(stdev(pdrs), 2),
            "TX_moyen": round(
                mean(r["TX"] for r in group), 2
            ),
            "RTT_moyen_ms": round(mean(rtts), 2)
            if rtts else ""
        })

save_csv("tp08_final_summary.csv", summary)

qualities = ["Q1", "Q2", "Q3"]
x = list(range(3))

plt.figure(figsize=(9, 5.5))
for mode, offset in (("CON", -0.2), ("NON", 0.2)):
    group = [r for r in summary if r["Mode"] == mode]
    plt.bar(
        [v + offset for v in x],
        [r["PDR_moyen"] for r in group],
        width=0.38, label=mode,
        yerr=[r["PDR_ecart_type"] for r in group],
        capsize=5
    )

plt.xticks(x, qualities)
plt.ylim(0, 115)
plt.ylabel("PDR applicatif (%)")
plt.xlabel("Qualite radio")
plt.title("TP08 - CoAP CON vs NON (3 seeds)")
plt.legend()
plt.grid(axis="y", alpha=0.25)
plt.tight_layout()
plt.savefig(
    out / "TP08_FINAL_PDR_CON_NON.png", dpi=200
)
plt.close()

con = [r for r in summary if r["Mode"] == "CON"]
plt.figure(figsize=(8, 5))
plt.plot(
    qualities,
    [r["RTT_moyen_ms"] for r in con],
    marker="o", linewidth=2
)
plt.ylabel("RTT moyen des reponses recues (ms)")
plt.xlabel("Qualite radio")
plt.title("TP08 - CoAP CON : RTT moyen")
plt.grid(alpha=0.25)
plt.tight_layout()
plt.savefig(out / "TP08_FINAL_RTT_CON.png", dpi=200)
plt.close()

print("\n===== RESUME FINAL TP08 =====")
for r in summary:
    print(
        f"{r['Mode']} {r['Qualite']} | "
        f"PDR={r['PDR_moyen']:.2f}% "
        f"+/- {r['PDR_ecart_type']:.2f} | "
        f"TX moyen={r['TX_moyen']:.1f} | "
        f"RTT={r['RTT_moyen_ms']}"
    )

print("\n18/18 LOGS ANALYSES")
print("4 FICHIERS FINAUX CREES")
