====
# STEP 9. Check where the model falls short (for the Limits section) (Natasha )
# ----------------------------------------------------------------------------
# A residual is how far an order's real freight was from the prediction.
#   - The plot shows whether misses grow for pricier shipments (a fan shape),
#     which is why I used robust standard errors in Step 6.
#   - The numbers back up the memo's claim that misses of R$50 or more are
#     rare (under 1%), nearly always higher than predicted, and mostly on
#     heavier packages.
# ============================================================================
step("STEP 9. How far off are the predictions?")

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
fig.savefig("Fp_residuals.png", dpi=150)
print("\nSaved Fp_residuals.png - look for the fan shape on the right.")


