
# --- STEP 5. Convert weight to kg and package size to liters ---
# Create df["weight_kg"] (grams / 1000) and df["volume_l"] (L x H x W / 1000)
# Print a summary of both columns
df["weight_kg"] = df["weight_g"] / 1000
df["volume_l"] = (df["length_cm"] * df["height_cm"] * df["width_cm"]) / 1000
print(df[["weight_kg","volume_l"]].describe())


# --- STEP 6. Fit the regression ---
# Freight on weight_kg + volume_l + state, Sao Paulo as baseline, HC3 errors
# Name the fitted model "model" and the state term "STATE" - later steps use them
# Also fit a version with size in cm (L + H + W) and compare R-squared
STATE = "C(customer_state, Treatment(reference='SP'))"
model = smf.ols(f"freight_value ~ weight_kg + volume_l + {STATE}",
                data=df).fit(cov_type="HC3")

df["dims_cm"] = df["length_cm"] + df["height_cm"] + df["width_cm"]
model_cm = smf.ols(f"freight_value ~ weight_kg + dims_cm + {STATE}",
                   data=df).fit(cov_type="HC3")

print(f"Rows used by the model: {int(model.nobs):,}")
print(
    f"R-squared with volume in liters:     {model.rsquared:.3f}   <- kept this one")
print(f"R-squared with total size in cm:     {model_cm.rsquared:.3f}")
print(f"Adjusted R-squared (kept model):     {model.rsquared_adj:.3f}")


# --- STEP 7. Coefficient table for the memo ---
# Estimate, std error, 95% CI for each coefficient; name the table "results"
# Rename state rows to "state_XX"; name the state-only rows "states"
# Print the memo rows, then all states vs. SP (most expensive first)
ci = model.conf_int()
results = pd.DataFrame({
    "estimate": model.params,
    "std_err": model.bse,
    "ci_low": ci[0],
    "ci_high": ci[1],
})
results.index = results.index.str.replace(
    r".*\[T\.(\w+)\]", r"state_\1", regex=True)

MEMO_ROWS = ["Intercept", "weight_kg", "volume_l", "state_RO", "state_RR",
             "state_AM", "state_BA", "state_MG", "state_RJ", "state_PR"]
print(results.loc[MEMO_ROWS].round(3).to_string())

print("\nAll states vs. Sao Paulo, most expensive first:")
states = results[results.index.str.startswith("state_")]
print(states.sort_values("estimate", ascending=False).round(2).to_string())



# --- STEP 8. Plain-language headline results ---
# Print the key numbers as sentences in reais (per kg, per liter, Rondonia,
# the four highest-cost states, and the R-squared as a percent)
kg, liter, ro = (results.loc[k] for k in ["weight_kg", "volume_l", "state_RO"])

print(f"Each extra kg adds about R${kg.estimate:.2f} "
      f"(95% CI R${kg.ci_low:.2f} to R${kg.ci_high:.2f}).")

print(f"Each extra liter adds about R${liter.estimate:.2f}, "
      f"or R${10 * liter.estimate:.2f} per 10 liters.")

print(f"Rondonia costs about R${ro.estimate:.2f} more than Sao Paulo for the same "
      f"package (95% CI R${ro.ci_low:.2f} to R${ro.ci_high:.2f}).")

top = states.sort_values("estimate", ascending=False).head(4)
top_names = ", ".join(name.replace("state_", "") for name in top.index)

print(f"The four highest-cost states ({top_names}) add about "
      f"R${top['estimate'].min():.0f} to R${top['estimate'].max():.0f} "
      f"more than Sao Paulo for the same package.")

print(f"Weight, size and destination explain {model.rsquared:.0%} of the "
      f"variation in freight.")


# --- STEP 9. How far off are the predictions? (residuals) ---
# Residual stats (median miss, misses of R$10+ and R$50+)
# Save the residual plot to OUTPUT_DIR / "Fp_residuals.png"
miss = model.resid
big = miss.abs() >= 50
heavy = df["weight_kg"] > 2
print(f"Half of orders miss by less than:  R${miss.abs().median():.2f}")
print(
    f"Miss by R$10 or more:              {(miss.abs() >= 10).mean():.1%} of orders")
print(
    f"Miss by R$50 or more:              {big.mean():.2%} of orders ({big.sum()})")
print(f"  ...of those, above prediction:   {(miss[big] > 0).mean():.1%}")
print(f"  ...of those, packages over 2 kg: {heavy[big].mean():.1%}")

fig, ax = plt.subplots(figsize=(6, 4))
ax.scatter(model.fittedvalues, miss, s=4, alpha=0.3)
ax.axhline(0, color="red", linewidth=1)
ax.set_xlabel("Predicted freight (R$)")
ax.set_ylabel("Actual minus predicted (R$)")
ax.set_title("Residuals vs. fitted")
fig.tight_layout()
fig.savefig(ROOT / "Fp_residuals.png", dpi=150)
print("\nSaved Fp_residuals.png - look for the fan shape on the right.")



