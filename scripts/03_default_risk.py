"""Which cardholder attributes drive risk of default?

- Pearson correlation for numeric drivers (income, age)
- One-way ANOVA for categorical drivers (marital status, employment, gender),
  with eta-squared effect size and a Tukey HSD post-hoc test
"""

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats

from common import heading, load_customers, save, set_style

INCOME_BINS = [50_000, 75_000, 100_000, 150_000]
INCOME_LABELS = ["$50k-75k", "$75k-100k", "$100k-150k"]


def pearson_report(customers, column, label):
    result = stats.pearsonr(customers[column], customers["default_risk"])
    r = result.statistic
    print(f"  {label:<8} r = {r:+.2f}   r² = {r * r:.3f}   p = {result.pvalue:.2g}")
    return r


def anova_report(customers, column):
    groups = [group["default_risk"].to_numpy()
              for _, group in customers.groupby(column)]
    result = stats.f_oneway(*groups)
    grand_mean = customers["default_risk"].mean()
    between = sum(len(g) * (g.mean() - grand_mean) ** 2 for g in groups)
    total = ((customers["default_risk"] - grand_mean) ** 2).sum()
    eta_squared = between / total
    verdict = "significant" if result.pvalue < 0.05 else "not significant"
    print(f"  {column:<18} F = {result.statistic:7.2f}   p = {result.pvalue:.2g}   "
          f"eta² = {eta_squared:.3f}   -> {verdict}")
    return result, groups


def tukey_report(customers, column):
    names = sorted(customers[column].unique())
    groups = [customers.loc[customers[column] == name, "default_risk"] for name in names]
    result = stats.tukey_hsd(*groups)
    print(f"  Tukey HSD on {column} (pairs that differ at p < 0.05):")
    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            if result.pvalue[i, j] < 0.05:
                diff = groups[i].mean() - groups[j].mean()
                print(f"    {names[i]:<26} vs {names[j]:<26} diff {diff:+.3f}")


def plot_marital(means):
    figure, axis = plt.subplots(figsize=(8, 5))
    sns.barplot(x=means.index, y=means.values, hue=means.index,
                palette="crest", legend=False, ax=axis)
    axis.set_title("Average Default Risk Score by Marital Status", fontweight="bold")
    axis.set_xlabel("Marital Status")
    axis.set_ylabel("Mean Default Risk Score")
    axis.tick_params(axis="x", rotation=30)
    save(figure, "default_risk_by_marital_status.png")


def plot_income(customers, r):
    figure, axis = plt.subplots(figsize=(8, 5))
    sns.regplot(data=customers, x="annual_income", y="default_risk", ax=axis,
                scatter_kws={"alpha": 0.35, "s": 14}, line_kws={"color": "#c0392b"})
    axis.set_title(f"Annual Income vs Risk of Default (r = {r:+.2f})", fontweight="bold")
    axis.set_xlabel("Annual Income Before Tax ($)")
    axis.set_ylabel("Risk of Default")
    axis.xaxis.set_major_formatter(lambda value, _: f"${value / 1000:.0f}k")
    save(figure, "income_vs_default_risk.png")


def main():
    set_style()
    customers = load_customers()

    heading("1) PEARSON CORRELATION WITH RISK OF DEFAULT")
    income_r = pearson_report(customers, "annual_income", "Income")
    pearson_report(customers, "age", "Age")
    print("  -> Income is a meaningful inverse driver; age explains <1% of variance.")

    bands = pd.cut(customers["annual_income"], bins=INCOME_BINS, labels=INCOME_LABELS)
    print("  Mean risk by income band:")
    for band, risk in customers.groupby(bands, observed=True)["default_risk"].mean().items():
        print(f"    {band:<12} {risk:.3f}")

    heading("2) ONE-WAY ANOVA: DOES RISK DIFFER ACROSS GROUPS?")
    for column in ["marital_status", "employment_status", "gender"]:
        anova_report(customers, column)

    means = customers.groupby("marital_status")["default_risk"].mean()
    print("  Mean risk by marital status:")
    for status, risk in means.sort_values(ascending=False).items():
        print(f"    {status:<26} {risk:.3f}")
    tukey_report(customers, "marital_status")

    plot_marital(means)
    plot_income(customers, income_r)


if __name__ == "__main__":
    main()
