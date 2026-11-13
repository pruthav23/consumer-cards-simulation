"""Benchmark Kharismo's fees against 3 Citi cards and 12 cards from 4 rival banks."""

import matplotlib.pyplot as plt
import seaborn as sns

from common import heading, load_industry, save, set_style

RECOMMENDED_OVERSEAS_CHARGE = 0.18
BANK_ORDER = ["Citi", "Bank 1", "Bank 2", "Bank 3", "Bank 4"]
PALETTE = dict(zip(BANK_ORDER, ["#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00"]))
MARKERS = dict(zip(BANK_ORDER, ["o", "X", "s", "P", "D"]))


def label_of(row):
    return f"Citi {row.card}" if row.bank == "Citi" else f"{row.bank[-1]} {row.card}"


def pricing_scatter(industry, y_column, y_label, filename, title):
    figure, axis = plt.subplots(figsize=(10, 5))
    plot_data = industry.assign(pct=industry[y_column] * 100)
    sns.scatterplot(data=plot_data, x="annual_fee", y="pct", hue="bank", style="bank",
                    hue_order=BANK_ORDER, style_order=BANK_ORDER,
                    palette=PALETTE, markers=MARKERS, s=140, ax=axis)
    for row in plot_data.itertuples():
        axis.annotate(label_of(row), (row.annual_fee, row.pct),
                      xytext=(8, 2), textcoords="offset points", fontsize=9)
    axis.set_title(title, fontweight="bold")
    axis.set_xlabel("Annual Fee ($)")
    axis.set_ylabel(y_label)
    axis.legend(title="Bank", loc="upper left", bbox_to_anchor=(1.01, 1))
    return figure, axis


def main():
    set_style()
    industry = load_industry()
    rivals = industry[industry["bank"] != "Citi"]
    kharismo = industry[industry["card"] == "Kharismo"].iloc[0]

    heading("1) PRICING BY BANK (rival banks averaged over their 3 cards)")
    summary = industry.groupby("bank")[["annual_fee", "local_cash_charge",
                                        "overseas_cash_charge"]].mean()
    print(summary.reindex(BANK_ORDER).round(3).to_string())

    heading("2) KHARISMO'S OVERSEAS CASH CHARGE")
    ranked = industry.sort_values("overseas_cash_charge", ascending=False)
    current_rank = list(ranked["card"] + ranked["bank"]).index("KharismoCiti") + 1
    print(f"  Kharismo charges {kharismo.overseas_cash_charge:.1%}: "
          f"#{current_rank} most expensive of {len(industry)} cards")
    print(f"  Rival average {rivals.overseas_cash_charge.mean():.1%}, "
          f"rival median {rivals.overseas_cash_charge.median():.1%}, "
          f"market average {industry.overseas_cash_charge.mean():.1%}")

    others = industry[industry["card"] != "Kharismo"]
    new_rank = (others["overseas_cash_charge"] > RECOMMENDED_OVERSEAS_CHARGE).sum() + 1
    print(f"  At the recommended {RECOMMENDED_OVERSEAS_CHARGE:.0%}: "
          f"#{new_rank} of {len(industry)} (mid-market), still below Citi A "
          f"({industry.query('card == \"A\" and bank == \"Citi\"').overseas_cash_charge.iloc[0]:.1%}) "
          f"and Citi B so the premium cards keep their positioning")

    heading("3) CHARTS")
    figure, _ = pricing_scatter(
        industry, "local_cash_charge", "Local Cash Charge (%)",
        "competitor_local_cash_pricing.png",
        "Industry Competitor Pricing: Annual Fee vs Local Cash Withdrawal Charge (%)")
    save(figure, "competitor_local_cash_pricing.png")

    figure, axis = pricing_scatter(
        industry, "overseas_cash_charge", "Overseas Cash Charge (%)",
        "competitor_overseas_cash_pricing.png",
        "Annual Fee vs Overseas Cash Withdrawal Charge (%)")
    axis.annotate("", xy=(kharismo.annual_fee, RECOMMENDED_OVERSEAS_CHARGE * 100),
                  xytext=(kharismo.annual_fee, kharismo.overseas_cash_charge * 100 - 0.4),
                  arrowprops={"arrowstyle": "->", "color": "#e41a1c", "lw": 1.8})
    axis.scatter([kharismo.annual_fee], [RECOMMENDED_OVERSEAS_CHARGE * 100],
                 s=140, facecolors="none", edgecolors="#e41a1c", linewidths=2)
    axis.annotate("Recommended 18%", (kharismo.annual_fee, RECOMMENDED_OVERSEAS_CHARGE * 100),
                  xytext=(14, 2), textcoords="offset points", fontsize=9,
                  color="#e41a1c", ha="left", va="bottom")
    axis.axhline(rivals.overseas_cash_charge.mean() * 100, color="grey",
                 linestyle="--", linewidth=1)
    axis.text(1010, rivals.overseas_cash_charge.mean() * 100 + 0.3,
              "rival average", color="grey", fontsize=9, ha="right")
    save(figure, "competitor_overseas_cash_pricing.png")


if __name__ == "__main__":
    main()
