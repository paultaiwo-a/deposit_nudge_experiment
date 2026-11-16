"""Run the project steps."""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(args: list[str], cwd: Path | None = None) -> None:
    """Run a command in the project environment and stop if it fails."""
    completed = subprocess.run(["uv", "run", *args], cwd=cwd or ROOT)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)


def data() -> None:
    run(["python", "scripts/load_data.py"])


def dbt() -> None:
    run(["dbt", "build", "--profiles-dir", "."], cwd=ROOT / "dbt")


def test() -> None:
    run(["pytest"])


def lint() -> None:
    run(["ruff", "check", "."])
    run(["ruff", "format", "--check", "."])


def readout() -> None:
    run(["python", "scripts/run_analysis.py"])
    run(["python", "scripts/peeking_simulation.py"])
    run(["python", "scripts/uplift.py"])


def all_steps() -> None:
    data()
    dbt()
    test()
    readout()


COMMANDS = {
    "data": data,
    "dbt": dbt,
    "test": test,
    "lint": lint,
    "readout": readout,
    "all": all_steps,
}


def main() -> None:
    names = "|".join(COMMANDS)
    if len(sys.argv) != 2 or sys.argv[1] not in COMMANDS:
        print(f"Usage: python run.py <{names}>", file=sys.stderr)
        raise SystemExit(1)
    COMMANDS[sys.argv[1]]()


if __name__ == "__main__":
    main()
