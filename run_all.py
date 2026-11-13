"""Run every analysis step and save the printed results to results/analysis_output.txt."""

import contextlib
import io
import runpy
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCRIPTS = [
    "01_portfolio_summary.py",
    "02_spend_seasonality.py",
    "03_default_risk.py",
    "04_competitor_pricing.py",
]


def main():
    sys.path.insert(0, str(ROOT / "scripts"))
    buffer = io.StringIO()
    for script in SCRIPTS:
        with contextlib.redirect_stdout(buffer):
            print(f"\n##### {script}")
            runpy.run_path(str(ROOT / "scripts" / script), run_name="__main__")

    output = buffer.getvalue().lstrip()
    print(output)
    results_dir = ROOT / "results"
    results_dir.mkdir(exist_ok=True)
    (results_dir / "analysis_output.txt").write_text(output)
    print("Saved results/analysis_output.txt")


if __name__ == "__main__":
    main()
