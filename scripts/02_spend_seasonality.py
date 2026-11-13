"""Monthly spend across the 12 spending cycles, split by channel."""

import matplotlib.pyplot as plt

from common import heading, load_customers, monthly_spend_by_channel, save, set_style

MARKERS = ["o", "s", "^", "d"]


def plot_monthly_breakdown(table):
    figure, axis = plt.subplots(figsize=(10, 5))
    for column, marker in zip(table.columns, MARKERS):
        axis.plot(table.index, table[column], marker=marker, linewidth=2, label=column)
    axis.set_title("Kharismo Card — Monthly Spend Breakdown ($)", fontweight="bold")
    axis.set_xlabel("Month")
    axis.set_ylabel("Total Spend ($)")
    axis.yaxis.set_major_formatter(lambda value, _: f"{value / 1e6:.2f}M")
    axis.tick_params(axis="x", rotation=45)
    axis.legend(loc="upper center", bbox_to_anchor=(0.5, -0.28), ncol=4, frameon=False)
    save(figure, "monthly_spend_breakdown.png")


def main():
    set_style()
    customers = load_customers()
    table = monthly_spend_by_channel(customers)
    monthly_total = table.sum(axis=1)

    heading("SPEND SEASONALITY (12 monthly cycles)")
    for month, total in monthly_total.items():
        bar = "#" * int(total / 1e5)
        print(f"  {month:<10} ${total / 1e6:5.2f}M  {bar}")
    top_two = monthly_total.nlargest(2)
    print(f"  Peaks: {top_two.index[0]} (${top_two.iloc[0] / 1e6:.2f}M), "
          f"{top_two.index[1]} (${top_two.iloc[1] / 1e6:.2f}M)")
    print(f"  Lowest: {monthly_total.idxmin()} (${monthly_total.min() / 1e6:.2f}M)")

    overseas = table["Overseas Transactions"]
    print(f"  Overseas transactions: ${overseas.min() / 1e6:.2f}M ({overseas.idxmin()}) "
          f"to ${overseas.max() / 1e6:.2f}M ({overseas.idxmax()}), "
          f"{overseas.max() / overseas.min():.1f}x swing -> travel seasonality")

    plot_monthly_breakdown(table)


if __name__ == "__main__":
    main()
