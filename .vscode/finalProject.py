"""
BAN5003 Final Project - Freight shipping costs between regions (Olist)

Decision supported: which destination states should receive a discounted
shipping rate, based on how much more freight each state adds than
Sao Paulo for the same package.

What this script does:
  1. Connects to the Olist database.
  2. Counts orders at each filter (delivered, single-item, valid measurements).
  3. Pulls delivered, single-item orders with valid weight and dimensions,
     and checks the row count against step 2.
  4. Checks the data (missing values, freight summary, free-shipping orders,
     freight above item price, date range, orders per state).
  5. Converts weight to kilograms and package size to liters.
  6. Fits a linear regression of freight value on weight, volume, and
     destination state (Sao Paulo as the baseline, robust standard errors).
  7. Builds the coefficient table: each state's extra freight vs. Sao Paulo
     with 95% intervals.
  8. Prints the headline results in plain language (reais).
  9. Checks how far off the predictions are and saves a residual plot
     (Fp_residuals.png).
 10. Checks whether weight and volume overlap too much (VIF).
 11. Refits without unusual freight orders to see if the answer changes.

Requires:
  - Python packages: pandas, statsmodels, sqlalchemy, psycopg2-binary, matplotlib
  - A local PostgreSQL database named BAN5003 with the olist tables loaded
    (schema "olist"). Edit ENGINE_URL if your database name or user differs.

Run (from the project folder, using a Python that has the packages above):
  python .vscode/finalProject.py
"""
# autopep8: off
# --- Load the libraries we need ---
from sqlalchemy import create_engine, text   # talks to the database
import pandas as pd                          # works with tables of data
import statsmodels.api as sm                 # needed for the VIF check
import statsmodels.formula.api as smf        # runs regression models
from statsmodels.stats.outliers_influence import variance_inflation_factor  # VIF
import matplotlib
matplotlib.use("Agg")   # save the chart to a file instead of opening a window
import matplotlib.pyplot as plt              # makes charts (after the backend is set)
# autopep8: on

# --- STEP 1. Connect to the database ---
# Where the database lives: on this computer, port 5432, named BAN5003
ENGINE_URL = "postgresql+psycopg2://localhost:5432/BAN5003"
engine = create_engine(ENGINE_URL)


# --- STEP 2. Count how many orders we keep at each filtering step ---
# 1. Orders that were delivered
# 2. Of those, orders with only one item
# 3. Of those, products with real (non-zero) weight and size
COUNTS_SQL = """
WITH delivered AS (
    SELECT order_id FROM olist.orders WHERE order_status = 'delivered'
),
single_item AS (
    SELECT order_id FROM olist.order_items GROUP BY order_id HAVING COUNT(*) = 1
)
SELECT
    (SELECT COUNT(*) FROM delivered) AS n_delivered,
    (SELECT COUNT(*) FROM delivered d JOIN single_item s ON d.order_id = s.order_id)
        AS n_single_item,
    (SELECT COUNT(*)
       FROM delivered d
       JOIN single_item s        ON d.order_id = s.order_id
       JOIN olist.order_items oi ON d.order_id = oi.order_id
       JOIN olist.products p     ON oi.product_id = p.product_id
      WHERE p.product_weight_g > 0 AND p.product_length_cm > 0
        AND p.product_height_cm > 0 AND p.product_width_cm > 0) AS n_final
"""
# Run the count query and grab the single row of results
with engine.connect() as conn:
    counts = pd.read_sql(text(COUNTS_SQL), conn).iloc[0]

# Turn the three counts into plain whole numbers
n_delivered, n_single, n_final = (int(counts[c]) for c in
                                  ["n_delivered", "n_single_item", "n_final"])

# Print how many orders are left after each step
print(f"Delivered orders:                       {n_delivered:,}")
print(
    f"  minus multi-item orders ({n_delivered - n_single:,}):      {n_single:,}")
print(f"  minus zero/missing measurements ({n_single - n_final}): {n_final:,}")


# --- STEP 3. Pull the actual data we will analyze ---
# Same filters as above, but this time we grab the columns we need:
# price, shipping cost (freight), product size/weight, and customer state
QUERY = """
SELECT
    o.order_id,
    oi.order_item_id,
    o.order_purchase_timestamp,
    oi.price::numeric             AS price,
    oi.freight_value::numeric     AS freight_value,
    p.product_weight_g::numeric   AS weight_g,
    p.product_length_cm::numeric  AS length_cm,
    p.product_height_cm::numeric  AS height_cm,
    p.product_width_cm::numeric   AS width_cm,
    c.customer_state
FROM olist.orders o
JOIN olist.order_items oi ON oi.order_id   = o.order_id
JOIN olist.products    p  ON p.product_id  = oi.product_id
JOIN olist.customers   c  ON c.customer_id = o.customer_id
WHERE o.order_status = 'delivered'
  AND o.order_id IN (SELECT order_id FROM olist.order_items
                     GROUP BY order_id HAVING COUNT(*) = 1)
  AND p.product_weight_g  > 0
  AND p.product_length_cm > 0
  AND p.product_height_cm > 0
  AND p.product_width_cm  > 0
"""
df = pd.read_sql(QUERY, engine)   # load the results into a table called df

# Make sure the number columns are regular decimal numbers Python can do math on
NUMERIC_COLS = ["price", "freight_value",
                "weight_g", "length_cm", "height_cm", "width_cm"]
df[NUMERIC_COLS] = df[NUMERIC_COLS].astype(float)   # Decimal -> float


# --- STEP 3 (cont.). Double-check we got the right number of rows ---
# If the row count doesn't match the count from before, stop the script
print(f"Rows pulled: {len(df):,}   Rows expected from Step 2: {n_final:,}")
assert len(df) == n_final, "Row count mismatch - check the joins before modeling."
print("Match. The pull is complete and has no duplicate rows.")


# --- STEP 4. Quick look at the data ---
# Are any values missing?
print("Missing values per column:")
print(df.isna().sum().to_string())

# Basic stats on shipping cost (average, min, max, etc.)
print("\nFreight value summary (R$):")
print(df["freight_value"].describe().round(2).to_string())

# How many orders shipped for free?
print(f"\nOrders with free shipping (R$0): {(df['freight_value'] == 0).sum()}")

# How many orders paid more for shipping than for the item itself?
print(
    f"Orders where freight exceeds item price: {(df['freight_value'] > df['price']).sum():,}")

# Cheapest item in the sample
print(f"Minimum item price (R$): {df['price'].min():.2f}")

# Date range the orders cover
print(f"First order: {df['order_purchase_timestamp'].min()}")
print(f"Last order:  {df['order_purchase_timestamp'].max()}")

# Which 5 states have the fewest orders?
print("\nOrders per state (fewest first):")
print(df["customer_state"].value_counts().sort_values().head(5).to_string())


# --- STEP 5. Convert weight to kg and package size to liters ---
# Create df["weight_kg"] (grams / 1000) and df["volume_l"] (L x H x W / 1000)
# Print a summary of both columns


# --- STEP 6. Fit the regression ---
# Freight on weight_kg + volume_l + state, Sao Paulo as baseline, HC3 errors
# Name the fitted model "model" and the state term "STATE" - later steps use them
# Also fit a version with size in cm (L + H + W) and compare R-squared


# --- STEP 7. Coefficient table for the memo ---
# Estimate, std error, 95% CI for each coefficient; name the table "results"
# Rename state rows to "state_XX"; name the state-only rows "states"
# Print the memo rows, then all states vs. SP (most expensive first)


# --- STEP 8. Plain-language headline results ---
# Print the key numbers as sentences in reais (per kg, per liter, Rondonia,
# the four highest-cost states, and the R-squared as a percent)


# --- STEP 9. How far off are the predictions? (residuals) ---
# Residual stats (median miss, misses of R$10+ and R$50+)
# Save the residual plot as Fp_residuals.png


# --- STEP 10. Are weight and volume too tangled together? (VIF) ---
# VIF for weight_kg and volume_l, plus their correlation
X = sm.add_constant(df[["weight_kg", "volume_l"]])
vif = pd.DataFrame({
    "variable": X.columns,
    "VIF": [variance_inflation_factor(X.values, i) for i in range(X.shape[1])],
})
print(vif[vif["variable"] != "const"].round(2).to_string(index=False))
print(f"\nCorrelation between weight and volume: "
      f"{df['weight_kg'].corr(df['volume_l']):.2f}")
print("Rule of thumb: under 5 is fine, over 10 is a problem.")


# --- STEP 11. Do the odd freight orders change the answer? ---
# Refit without R$0 freight / freight > price / both, compare state effects
FORMULA = f"freight_value ~ weight_kg + volume_l + {STATE}"

versions = {
    "All orders":              df,
    "Without R$0 freight":     df[df["freight_value"] > 0],
    "Without freight > price": df[df["freight_value"] <= df["price"]],
    "Without either":          df[(df["freight_value"] > 0)
                                  & (df["freight_value"] <= df["price"])],
}

state_effects = {}
for label, data in versions.items():
    fit = smf.ols(FORMULA, data=data).fit(cov_type="HC3")
    effects = fit.params[fit.params.index.str.contains(r"\[T\.")]
    effects.index = effects.index.str.extract(r"\[T\.(\w+)\]")[0]
    state_effects[label] = effects
    print(f"{label:<26} rows: {len(data):,}   adj R2: {fit.rsquared_adj:.3f}")

compare = pd.DataFrame(state_effects).rename_axis(None).round(2)
print("\nExtra freight vs Sao Paulo (R$), for the top states:")
print(compare.loc[["RO", "AC", "PB", "RR", "MA"]].to_string())
