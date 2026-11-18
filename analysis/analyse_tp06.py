
import re
import csv
import statistics
from pathlib import Path

folder = Path(__file__).resolve().parent
logfile = folder / "tp06_logs.txt"

tx = set()
rx = set()
ack = {}
timeouts = set()

for line in logfile.read_text(errors="replace").splitlines():
    m = re.search(
        r"TEMP_(TX|RX)\s+id=(\d+),seq=(\d+)", line
    )
    if m:
        key = (int(m.group(2)), int(m.group(3)))
        if m.group(1) == "TX":
            tx.add(key)
        else:
            rx.add(key)

    m = re.search(
        r"TEMP_ACK\s+id=(\d+)\s+seq=(\d+)\s+rtt_ms=(\d+)",
        line
    )
    if m:
        ack[(int(m.group(1)), int(m.group(2)))] = int(m.group(3))

    m = re.search(
        r"TEMP_TIMEOUT\s+id=(\d+)\s+seq=(\d+)", line
    )
    if m:
        timeouts.add((int(m.group(1)), int(m.group(2))))

if not tx:
    raise SystemExit("No TEMP_TX messages found in the log.")

received = tx & rx
successful = tx & ack.keys()
rtts = [ack[key] for key in successful]

pdr = 100 * len(received) / len(tx)
success_rate = 100 * len(successful) / len(tx)

print("=== TP06 PERFORMANCE ===")
print("TX:", len(tx))
print("RX uniques:", len(received))
print("Transactions ACK:", len(successful))
print("Timeouts observed:", len(tx & timeouts))
print(f"PDR: {pdr:.2f}%")
print(f"Success Rate: {success_rate:.2f}%")
print(f"Packet Loss: {100 - pdr:.2f}%")

if rtts:
    print(f"RTT moyen: {statistics.mean(rtts):.2f} ms")
    print(f"RTT median: {statistics.median(rtts):.2f} ms")

with (folder / "tp06_messages.csv").open("w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow([
        "node_id", "seq", "server_received",
        "ack_received", "timeout", "rtt_ms"    ])
    for key in sorted(tx):
        writer.writerow([
            key[0], key[1],
            int(key in rx),
            int(key in ack),
            int(key in timeouts),
            ack.get(key, "")
        ])

print("CSV saved: tp06_messages.csv")
