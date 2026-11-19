
import re
import csv
import statistics
import argparse
from pathlib import Path

parser = argparse.ArgumentParser(
    description="Analyze TP06 CoAP performance logs"
)
parser.add_argument("--log", type=Path, required=True)
parser.add_argument("--output", type=Path, required=True)
args = parser.parse_args()

logfile = args.log.expanduser().resolve()
output = args.output.expanduser().resolve()

if not logfile.is_file():
    parser.error(f"Log file not found: {logfile}")

output.parent.mkdir(parents=True, exist_ok=True)

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

with output.open("w", newline="", encoding="utf-8") as f:
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

print(f"CSV saved: {output}")
