"""Sales Data Analysis Dashboard (Pandas + NumPy + Matplotlib).
Run: python generate_data.py   (once)   then   python dashboard.py
Outputs: charts in ./output/ and a combined dashboard.png"""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")            # works without a display; remove this line to use plt.show()
import matplotlib.pyplot as plt

OUT = "output"
os.makedirs(OUT, exist_ok=True)

# ---------- 1. LOAD ----------
df = pd.read_csv("sales_data.csv")
print("Raw shape:", df.shape)

# ---------- 2. CLEAN ----------
df = df.drop_duplicates()
df["region"] = df["region"].fillna("Unknown")
df["customer_age"] = df["customer_age"].fillna(df["customer_age"].median())
df["order_date"] = pd.to_datetime(df["order_date"])
print("Clean shape:", df.shape)

# ---------- 3. FEATURE ENGINEERING ----------
df["revenue"] = df["unit_price"] * df["quantity"] * (1 - df["discount_pct"] / 100)
df["month"] = df["order_date"].dt.to_period("M")
df["weekday"] = df["order_date"].dt.day_name()
df["age_group"] = pd.cut(df["customer_age"], bins=[17, 25, 35, 45, 65],
                         labels=["18-25", "26-35", "36-45", "46-65"])

# ---------- 4. ANALYSIS ----------
monthly = df.groupby("month")["revenue"].sum()
by_category = df.groupby("category")["revenue"].sum().sort_values(ascending=False)
by_region = df.groupby("region")["revenue"].sum().sort_values(ascending=False)
top_products = df.groupby("product")["revenue"].sum().nlargest(8).sort_values()
by_age = df.groupby("age_group", observed=True)["revenue"].mean()
weekday_order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
by_weekday = df.groupby("weekday")["revenue"].sum().reindex(weekday_order)
discount_effect = df.groupby("discount_pct")["quantity"].mean()

growth = monthly.pct_change().dropna() * 100
corr = df[["unit_price", "quantity", "discount_pct", "customer_age", "revenue"]].corr()

print("\n===== KEY INSIGHTS =====")
print(f"Total revenue        : Rs {df['revenue'].sum():,.0f}")
print(f"Average order value  : Rs {df['revenue'].mean():,.0f}")
print(f"Best category        : {by_category.index[0]} (Rs {by_category.iloc[0]:,.0f})")
print(f"Best region          : {by_region.index[0]}")
print(f"Best month           : {monthly.idxmax()} (Rs {monthly.max():,.0f})")
print(f"Best weekday         : {by_weekday.idxmax()}")
print(f"Avg monthly growth   : {np.mean(growth):.2f}%  (std {np.std(growth):.2f})")
print(f"Revenue-quantity corr: {corr.loc['revenue', 'quantity']:.2f}")


# ---------- 5. CHARTS ----------
def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=130)
    plt.close(fig)


def draw_monthly(ax):
    ax.plot(monthly.index.astype(str), monthly.values, marker="o", color="#2a6fdb")
    ax.set_title("Monthly Revenue Trend")
    ax.set_ylabel("Revenue (Rs)")
    ax.tick_params(axis="x", rotation=60, labelsize=7)
    ax.grid(alpha=0.3)


def draw_category(ax):
    ax.pie(by_category.values, labels=by_category.index, autopct="%1.1f%%", startangle=90)
    ax.set_title("Revenue Share by Category")


def draw_region(ax):
    ax.bar(by_region.index, by_region.values, color="#3aa17e")
    ax.set_title("Revenue by Region")
    ax.set_ylabel("Revenue (Rs)")


def draw_products(ax):
    ax.barh(top_products.index, top_products.values, color="#e07b39")
    ax.set_title("Top 8 Products by Revenue")


def draw_weekday(ax):
    ax.bar([d[:3] for d in weekday_order], by_weekday.values, color="#8e5bd6")
    ax.set_title("Revenue by Weekday")


def draw_heatmap(ax):
    im = ax.imshow(corr.values, cmap="coolwarm", vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr)), corr.columns, rotation=45, ha="right", fontsize=8)
    ax.set_yticks(range(len(corr)), corr.columns, fontsize=8)
    for i in range(len(corr)):
        for j in range(len(corr)):
            ax.text(j, i, f"{corr.values[i, j]:.2f}", ha="center", va="center", fontsize=7)
    ax.set_title("Correlation Heatmap")
    return im


charts = {"monthly_revenue.png": draw_monthly, "category_share.png": draw_category,
          "region_revenue.png": draw_region, "top_products.png": draw_products,
          "weekday_revenue.png": draw_weekday, "correlation.png": draw_heatmap}

for fname, fn in charts.items():            # individual charts
    fig, ax = plt.subplots(figsize=(7, 4.5))
    fn(ax)
    save(fig, fname)

fig, axes = plt.subplots(2, 3, figsize=(18, 10))   # combined dashboard
for ax, fn in zip(axes.ravel(), charts.values()):
    fn(ax)
fig.suptitle("Sales Analysis Dashboard", fontsize=20, fontweight="bold")
fig.tight_layout(rect=[0, 0, 1, 0.96])
fig.savefig("dashboard.png", dpi=110)
plt.close(fig)

df.to_csv(os.path.join(OUT, "cleaned_sales.csv"), index=False)
print("\nSaved: dashboard.png, charts and cleaned_sales.csv in ./output/")
