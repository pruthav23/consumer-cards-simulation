"""Year-1 portfolio KPIs and cardholder demographics for Citi Kharismo."""

import pandas as pd

from common import CHANNELS, heading, load_customers, spend_columns

AGE_BANDS = [(18, 25), (26, 35), (36, 45), (46, 65), (66, 120)]
AGE_LABELS = ["18-25", "26-35", "36-45", "46-65", "Over 65"]
INCOME_BINS = [50_000, 75_000, 100_000, 150_000]
INCOME_LABELS = ["$50k-75k", "$75k-100k", "$100k-150k"]


def main():
    customers = load_customers()

    heading("1) PORTFOLIO KPIs")
    total_spend = customers[spend_columns()].to_numpy().sum()
    print(f"  Active accounts:            {len(customers):,}")
    print(f"  Total 12-month spend:       ${total_spend:,.0f}  (${total_spend / 1e6:.2f}M)")
    print(f"  Spend per cardholder:       ${total_spend / len(customers):,.0f}")
    for channel, label in CHANNELS.items():
        channel_total = customers[spend_columns(channel=channel)].to_numpy().sum()
        print(f"    {label:<22} ${channel_total / 1e6:6.2f}M  "
              f"({channel_total / total_spend:.1%})")
    print(f"  Mean risk of default:       {customers['default_risk'].mean():.3f}")
    print(f"  Total default exposure:     ${customers['default_amount'].sum():,.0f}")

    heading("2) CARDHOLDER DEMOGRAPHICS")
    ages = pd.cut(customers["age"], bins=[17, 25, 35, 45, 65, 120], labels=AGE_LABELS)
    print("  Age bands:")
    for label, share in ages.value_counts(normalize=True).reindex(AGE_LABELS).items():
        print(f"    {label:<10} {share:6.1%}")
    print(f"  Aged over 45: {(customers['age'] > 45).mean():.1%}")

    incomes = pd.cut(customers["annual_income"], bins=INCOME_BINS, labels=INCOME_LABELS)
    print("  Income bands:")
    for label, count in incomes.value_counts().reindex(INCOME_LABELS).items():
        print(f"    {label:<12} {count:4d} accounts ({count / len(customers):.1%})")

    print("  Employment status:")
    for status, share in customers["employment_status"].value_counts(normalize=True).items():
        print(f"    {status:<22} {share:6.1%}")


if __name__ == "__main__":
    main()
