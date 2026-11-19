# Reproducing the Experimental Analysis

This guide explains how to regenerate the analysis outputs
from the original Contiki-NG/Cooja simulation logs.

## Requirements

- Python 3
- Matplotlib
- Contiki-NG and Cooja
- Original experimental logs or newly generated simulation logs

Validated Contiki-NG revision:

`c02eedae8b187123069891f81a7111b833701f9c`

## Data Availability

The repository includes:

- Cooja configurations in `simulations/`
- Application source code in `examples/`
- Published CSV datasets in `results/csv/`
- Published figures in `results/figures/`
- Analysis scripts in `analysis/`

The original raw simulation logs are not currently included.

Re-running the log parsers requires the original logs or
new logs generated with the supplied Cooja configurations.
New executions may produce different results depending on
the seed, environment and simulator configuration.

## Reproduction Commands

Run the following commands from the repository root.

Create a temporary directory to avoid overwriting
the published results:

```bash
OUT=$(mktemp -d)
echo "Output directory: $OUT"
```

### TP06: Multi-hop latency

```bash
python3 analysis/analyse_tp06.py \
  --log "$HOME/contiki-ng/results/tp06/tp06_logs.txt" \
  --output "$OUT/tp06_messages.csv"
```

Reference output:

`results/csv/tp06_messages.csv`

The captured log contains 13,334 unique transmissions,
13,333 server receptions and 13,333 observed responses.

Mean completed-exchange RTT: 146.11 ms.

One final transmission was unresolved at the end of the capture.
It is not considered a confirmed permanent packet loss.

### TP07: Scalability

```bash
python3 analysis/analyse_tp07.py \
  --logs-dir "$HOME/contiki-ng/results/tp07" \
  --output-dir "$OUT/tp07"
```

This analysis expects nine experiment logs:

- S1: 5 clients, 3 seeds
- S2: 10 clients, 3 seeds
- S3: 20 clients, 3 seeds

Published datasets:

- `results/csv/tp07_runs.csv`
- `results/csv/tp07_per_node.csv`

To regenerate plots from the published CSV:

```bash
MPLBACKEND=Agg python3 analysis/graphes_tp07.py \
  --output-dir "$OUT/tp07_figures"
```

### TP08: CON vs NON

```bash
python3 analysis/tp08_final.py \
  --logs-dir "$HOME/contiki-ng/results/tp08" \
  --output-dir "$OUT/tp08"
```

The final analysis expects 18 simulation logs:
2 CoAP modes, 3 radio conditions, and 3 random seeds.

Published datasets:

- `results/csv/tp08_final_runs.csv`
- `results/csv/tp08_final_summary.csv`

The script also generates:

- `TP08_FINAL_PDR_CON_NON.png`
- `TP08_FINAL_RTT_CON.png`

### TP08: Preliminary analysis

The preliminary analysis covers Q1 and Q2 only
(12 simulations). It is archived for reference.

```bash
python3 analysis/legacy/analyse_tp08_initial.py \
  --logs-dir "$HOME/contiki-ng/results/tp08" \
  --output-dir "$OUT/tp08_legacy"
```

Use `analysis/tp08_final.py` for the authoritative
published TP08 comparison.

## Validation Performed

Using the original experimental logs:

| Analysis | Validation |
|---|---|
| TP06 | Generated CSV matches published CSV |
| TP07 | Both generated CSV files match published CSV files |
| TP07 plots | Three plots generated successfully |
| TP08 final | Both generated CSV files match published CSV files |
| TP08 final plots | Two plots generated successfully |
| TP08 legacy | Common Q1/Q2 metrics match final analysis |

CSV comparisons were performed on parsed rows.
Plot generation was checked, but pixel-level image
equivalence was not established.

## Scientific Limitations

- The results describe simulated networks, not hardware.
- Each TP07/TP08 scenario uses three random seeds.
- CON and NON do not have identical traffic volumes in Q3.
- The logs do not independently quantify all lower-layer
  retransmissions.
- The observed response log marker `TEMP_ACK` must not be
  interpreted as a separately verified CoAP transport ACK.
