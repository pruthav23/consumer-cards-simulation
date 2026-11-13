"""Shared data loading and chart styling for the analysis scripts."""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
FIGURES_DIR = ROOT / "figures"

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]
MONTH_NAMES = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
CHANNELS = {
    "local_transaction": "Local Transactions",
    "local_cash": "Local Cash",
    "overseas_transaction": "Overseas Transactions",
    "overseas_cash": "Overseas Cash",
}


def load_customers():
    return pd.read_csv(DATA_DIR / "customers.csv")


def load_industry():
    return pd.read_csv(DATA_DIR / "industry_pricing.csv")


def spend_columns(channel=None, month=None):
    """Names of the monthly spend columns, optionally filtered."""
    months = [month] if month else MONTHS
    channels = [channel] if channel else list(CHANNELS)
    return [f"{m}_{c}" for m in months for c in channels]


def monthly_spend_by_channel(customers):
    """12 x 4 table: total portfolio spend per month and channel."""
    table = pd.DataFrame(
        {label: [customers[f"{month}_{channel}"].sum() for month in MONTHS]
         for channel, label in CHANNELS.items()},
        index=MONTH_NAMES,
    )
    return table


def set_style():
    sns.set_theme(style="whitegrid", context="notebook")


def save(figure, name):
    FIGURES_DIR.mkdir(exist_ok=True)
    path = FIGURES_DIR / name
    figure.savefig(path, dpi=200, bbox_inches="tight")
    plt.close(figure)
    print(f"  saved figures/{name}")


def heading(title):
    print()
    print("=" * 72)
    print(title)
    print("=" * 72)
