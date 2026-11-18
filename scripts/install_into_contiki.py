from pathlib import Path
import argparse
import filecmp
import shutil
import sys

parser = argparse.ArgumentParser(
    description="Install CoAP project into Contiki-NG"
)
parser.add_argument(
    "--contiki",
    default="~/contiki-ng",
    help="Path to Contiki-NG"
)
parser.add_argument(
    "--install",
    action="store_true",
    help="Copy missing files (never overwrite)"
)
args = parser.parse_args()

repo = Path(__file__).resolve().parent.parent
contiki = Path(args.contiki).expanduser().resolve()

if not (contiki / "tools/cooja").is_dir():
    sys.exit("ERROR: invalid Contiki-NG directory")

# Existing upstream dependencies
upstream = [
    "examples/hello-world/hello-world.c",
    "examples/rpl-udp/udp-server.c",
    "examples/rpl-udp/udp-client.c",
]

for relative in upstream:
    if not (contiki / relative).is_file():
        sys.exit(f"ERROR: upstream file missing: {relative}")

# Project files to install
files = []

for tp in ("tp04", "tp05", "tp06", "tp07", "tp08"):
    folder = repo / "examples" / tp
    files.extend(p for p in folder.rglob("*") if p.is_file())

files.extend((repo / "simulations").glob("*.csc"))

identical = []
missing = []
conflicts = []

for source in files:
    relative = source.relative_to(repo)
    target = contiki / relative

    if target.is_file():
        if filecmp.cmp(source, target, shallow=False):
            identical.append(relative)
        else:
            conflicts.append(relative)
    elif target.exists():
        conflicts.append(relative)
    else:
        missing.append((source, target))

print("===== INSTALLATION CHECK =====")
print("Contiki-NG :", contiki)
print("Project files :", len(files))
print("Already identical :", len(identical))
print("Missing :", len(missing))
print("Conflicts :", len(conflicts))

if conflicts:
    for item in conflicts:
        print("[CONFLICT]", item)
    sys.exit("STOP: existing files differ. Nothing copied.")

if args.install:
    for source, target in missing:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)
        print("[INSTALLED]", source.relative_to(repo))
    print("INSTALLATION OK")
else:
    print("CHECK OK - no files modified")
