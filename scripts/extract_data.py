"""Extract the raw input tables from the Forage workbook into CSV files.

Only the raw inputs are exported: customer records, monthly spend and
competitor pricing. Formula-driven summary sheets are not.

Usage:
    python scripts/extract_data.py path/to/workbook.xlsx
"""

import sys
from pathlib import Path

import openpyxl
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

MONTHS = ["jan", "feb", "mar", "apr", "may", "jun",
          "jul", "aug", "sep", "oct", "nov", "dec"]
CHANNELS = ["local_cash", "local_transaction",
            "overseas_cash", "overseas_transaction"]
PROFILE_COLUMNS = ["customer_id", "age", "gender", "marital_status",
                   "employment_status", "annual_income", "monthly_payment_pct",
                   "credit_limit", "default_risk", "default_amount"]


def extract_customers(workbook):
    sheet = workbook["I. Customer Personal Data"]
    # Customer rows are the ones whose first cell is a numeric customer ID.
    # This skips headers and any totals row, whatever the workbook version.
    rows = [list(row) for row in sheet.iter_rows(values_only=True)
            if isinstance(row[0], (int, float))]

    spend_columns = [f"{month}_{channel}"
                     for month in MONTHS for channel in CHANNELS]
    customers = pd.DataFrame([row[:10] for row in rows], columns=PROFILE_COLUMNS)
    spend = pd.DataFrame([row[11:59] for row in rows], columns=spend_columns)

    customers = pd.concat([customers, spend.round(2)], axis=1)
    for column in ["marital_status", "employment_status", "gender"]:
        customers[column] = customers[column].str.strip()
    customers["default_risk"] = customers["default_risk"].round(4)
    return customers


def extract_industry(workbook):
    sheet = workbook["I. Industry Data"]
    rows = [row[:5] for row in sheet.iter_rows(min_row=3, max_row=17,
                                               values_only=True)]
    industry = pd.DataFrame(rows, columns=["bank", "card", "annual_fee",
                                           "local_cash_charge",
                                           "overseas_cash_charge"])
    industry["bank"] = industry["bank"].ffill()
    industry["bank"] = industry["bank"].map(
        lambda value: "Citi" if value == "Citi" else f"Bank {int(value)}")
    industry[["local_cash_charge", "overseas_cash_charge"]] = (
        industry[["local_cash_charge", "overseas_cash_charge"]].round(4))
    return industry


def main():
    workbook = openpyxl.load_workbook(sys.argv[1], data_only=False)
    DATA_DIR.mkdir(exist_ok=True)

    customers = extract_customers(workbook)
    industry = extract_industry(workbook)

    customers.to_csv(DATA_DIR / "customers.csv", index=False)
    industry.to_csv(DATA_DIR / "industry_pricing.csv", index=False)
    print(f"Wrote {len(customers):,} customers and {len(industry)} cards to {DATA_DIR}")


if __name__ == "__main__":
    main()
