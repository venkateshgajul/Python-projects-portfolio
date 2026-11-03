"""Creates a realistic (synthetic) sales dataset: sales_data.csv.  Run: python generate_data.py
You can replace sales_data.csv with any real dataset (e.g. from Kaggle) that has similar columns."""
import numpy as np
import pandas as pd

rng = np.random.default_rng(42)
N = 5000

catalog = {
    "Electronics": {"Laptop": 55000, "Smartphone": 25000, "Headphones": 3000, "Smartwatch": 8000},
    "Clothing": {"T-Shirt": 600, "Jeans": 1800, "Jacket": 3500, "Sneakers": 2800},
    "Home": {"Mixer Grinder": 3200, "Bedsheet": 1200, "Lamp": 900, "Air Fryer": 6500},
    "Books": {"Python Book": 700, "Novel": 350, "Textbook": 900, "Comics": 250},
}
rows = [(c, p, price) for c, items in catalog.items() for p, price in items.items()]
pick = rng.integers(0, len(rows), N)

dates = pd.to_datetime("2024-01-01") + pd.to_timedelta(rng.integers(0, 730, N), unit="D")
month_boost = 1 + 0.4 * np.isin(dates.month, [10, 11, 12])   # festive-season bump
quantity = np.clip(rng.poisson(2 * month_boost), 1, None)

df = pd.DataFrame({
    "order_id": np.arange(1001, 1001 + N),
    "order_date": dates.strftime("%Y-%m-%d"),
    "region": rng.choice(["North", "South", "East", "West"], N, p=[0.25, 0.30, 0.15, 0.30]),
    "category": [rows[i][0] for i in pick],
    "product": [rows[i][1] for i in pick],
    "unit_price": [rows[i][2] for i in pick],
    "quantity": quantity,
    "discount_pct": rng.choice([0, 5, 10, 15, 20], N, p=[0.4, 0.2, 0.2, 0.1, 0.1]),
    "customer_age": rng.integers(18, 65, N).astype(float),
})

# Add some dirty data on purpose so the cleaning step in dashboard.py is meaningful
df.loc[rng.choice(N, 60, replace=False), "customer_age"] = np.nan
df.loc[rng.choice(N, 25, replace=False), "region"] = None
df = pd.concat([df, df.sample(30, random_state=1)], ignore_index=True)   # duplicate rows

df.to_csv("sales_data.csv", index=False)
print(f"Created sales_data.csv with {len(df)} rows")
