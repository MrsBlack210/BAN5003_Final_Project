# BAN5003 Final Project: Freight Costs Between States (Olist)

**Business question:** What makes shipping cost more on Olist, and by how much in reais?

**Decision supported:** Which destination states should get a discounted shipping rate, based on how much more freight each state adds than São Paulo for the same package.

Team name: QUANT LABS
```
Members and roles:
Natasha Black — project lead
Colton Russell/Brandon Gallegos — data lead
Faustino Esqueda/Brandon Gallegos — modeling lead
Mikayla Esqueda — communications lead
Brandon Gallegos — AI integration lead
VP of Olist Operations —
```

```
README.md            this file
requirements.txt     pinned Python packages
.env.example         template for your Postgres login (Path A only)
.gitignore
sql/                 the two SQL queries the script runs
src/                 the analysis script (finalProject.py)
data/                CSV extract of the main query (Path B)
outputs/             saved results (residual plot)
ai/prompts/          saved AI prompts and responses
```

---

## 1. Install

You need **Python 3.12**. We tested the setup in a plain new virtual environment, not Anaconda or Colab.

**macOS / Linux**

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

**Windows (PowerShell)**

```powershell
py -3.12 -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`requirements.txt` pins every package version, so you get the same environment we tested. The `.venv` folder isn't in the repo, so build your own with the steps above.

**Database login (Path A only):** copy `.env.example` to `.env` and fill in your own Postgres user and database name:

```bash
cp .env.example .env
```

```
DATABASE_URL=postgresql+psycopg2://your_user:your_password@localhost:5432/BAN5003
```

`.env` is git-ignored, so your login never gets committed. If you use Path B (the CSV), skip this step.

---

## 2. Data

**Source:** the course's Olist e-commerce dataset, loaded into Postgres under the schema `olist`. The queries use four tables: `orders`, `order_items`, `products` and `customers`.

**Two ways to get the data:**

|                  | How                                                                                                                       | What you need                                       |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------- |
| **Path A** | Load Olist into a local Postgres. The script runs `sql/01_filter_counts.sql` and `sql/02_freight_extract.sql` itself. | Postgres, the `olist` schema, and a `.env` file |
| **Path B** | Use `data/olist_freight_extract.csv`, the saved output of `sql/02_freight_extract.sql`.                               | Nothing beyond the Python install                   |

The extract has **86,825 rows**, one per order. It keeps only:

1. delivered orders,
2. with exactly one item per order (a shared shipping charge can't be tied to one product's weight or size),
3. where the product's weight and all three dimensions are above zero.

Both paths give identical results. We checked that Steps 3–4 print the same output with either one.

**Data notes:**

- **Filtering:** we started with 96,478 delivered orders, removed 9,635 multi-item orders (about 10%), and dropped 18 more for missing or zero measurements, leaving 86,825.
- **No missing values** in the final data.
- **Dates:** orders run from **Oct 3, 2016 to Aug 29, 2018**.
- **Unusual freight:** 300 orders have **R$0 freight** (free shipping), and **2,645** have freight above the item's price. We kept both. Step 11 refits the model without them to check that they don't change the results (they don't; see Results).
- **Small states:** some states have very few orders, such as Roraima (36), Amapá (57) and Acre (75), so their estimates are less certain.

---

## 3. Run

Run from the project folder, with the virtual environment active. There's only one script.

**Path A (Postgres):**

```bash
python src/finalProject.py
```

**Path B (CSV, no database needed):**

```bash
python src/finalProject.py --csv data/olist_freight_extract.csv
```

With `--csv`, the script skips the database. It reads the extract and checks it against the expected 86,825 rows. The filter counts in Step 2 need the database, so Path B skips them. The counts are listed in the Data section above.

**What you should see:**

1. The filter counts (Path A only) and the row-count check:
   ```
   Rows pulled: 86,825   Rows expected from Step 2: 86,825
   Match. The pull is complete and has no duplicate rows.
   ```
2. Data checks: missing values, a freight summary, unusual freight orders, the date range, and the states with the fewest orders.
3. The coefficient table: an estimate, standard error and 95% CI for weight, volume and every state compared with São Paulo.
4. The headline results in plain language, the residual checks, the VIF check, and the robustness refits.

**Where the outputs go:** the residual plot is saved to `outputs/Fp_residuals.png`. Everything else prints to the terminal.

[Team: remove this note once Steps 5–9 are in. Until then, the script stops at Step 10 with a `KeyError`, because Step 10 uses the `weight_kg` and `volume_l` columns that Step 5 creates.]

---

## 4. Results

**Main finding:** four states cost far more to ship to than São Paulo for the same package. **Rondônia (RO), Acre (AC), Paraíba (PB) and Roraima (RR)** each add about **R$26 to R$28** more freight than São Paulo, after accounting for the package's weight and size.

- **Example:** shipping to Rondônia costs about **R$27.51 more** than shipping the same package to São Paulo (95% CI: R$24.78 to R$30.24).
- **Weight:** each extra kilogram adds about **R$1.66** (95% CI: R$1.57 to R$1.75).
- **Size:** each extra liter of package volume adds about **R$0.19**, or about R$1.91 per 10 liters.

**Model fit:** weight, size and destination together explain about 54% of the variation in freight (**adjusted R² = 0.543**). A version that measured size in centimeters (length + height + width) fit worse (R² = 0.518), so we kept liters.

**Checks:**

- **Weight and volume overlap:** they're correlated (0.80), but the **VIF is 2.82** for each, well under the usual warning level of 5. The model can separate their effects.
- **Unusual freight orders:** dropping the R$0 freight orders, the orders with freight above the item price, or both, moved the top states' estimates by about R$2 at most. RO stayed between R$27.51 and R$27.97. Adjusted R² stayed between 0.543 and 0.551. Those orders don't change the conclusion.

**Limits (what would change the recommendation):**

- **Roraima and Acre rest on few orders** (36 and 75). Their intervals are wide (Roraima: R$19.16 to R$32.90). With more orders, either state could move up or down the ranking, so discounts for them should be reviewed as more data comes in.
- **Errors grow for heavier, costlier shipments, and mostly run above the prediction.** Half of orders are predicted within R$2.95, but 0.57% (499 orders) miss by R$50 or more. Of those, 94.6% cost more than predicted, and 81.2% are packages over 2 kg. The model is good for comparing regions, but it shouldn't be used to quote an exact shipping price, especially for heavy packages.

**Residual plot** (`outputs/Fp_residuals.png`): misses spread out as predicted freight rises (a fan shape). This is why the model uses robust (HC3) standard errors.

![Residuals vs. fitted](outputs/Fp_residuals.png)

**Changes from Stage 1:**

- The data window is now stated exactly: **Oct 3, 2016 to Aug 29, 2018**.
- The data quality counts are now exact and come from the SQL itself: 96,478 delivered, 9,635 multi-item removed, 18 with bad measurements removed, 86,825 kept, with 300 R$0 freight orders and 2,645 orders with freight above the item price.
- [Any other changes the team made since the proposal]

---

## 5. AI use

**Tool:** Claude Code (the VS Code extension), using the model **Claude Opus 5.5**. [Add any other tools the team used, such as ChatGPT or Copilot, with the model or plan.]

**What each person used it for:**

| Person           | What AI was used for                                                            | What stayed human-written                                                        |
| ---------------- | ------------------------------------------------------------------------------- | -------------------------------------------------------------------------------- |
| Brandon Gallegos | Creating comments, debugging code, creating the README, fixing format and typos | Base code, the base comments, the analysis design and SQL queries, python script |
| Mikayla Esqueda  | Reviewing code, understanding assignment requirements, GitHub guidance, and drafting and proofreading the business recommendation.                                                                                      | Personal revisions to the business recommendation and explanations of the analytical findings.|
| [Name]           | [What they used AI for]                                                         | [What they wrote themselves]                                                     |
| [Name]           | [What they used AI for]                                                         | [What they wrote themselves]                                                     |
| [Name]           | [What they used AI for]                                                         | [What they wrote themselves]                                                     |

**How we checked the AI's work:** every number in this README comes from running the script and was compared with the expected output. The AI's changes were reviewed before committing. [Edit this to match what the team actually did.]

**Saved prompts and responses:** see `ai/prompts/`.

- `ai/prompts/2026-11-24_claude_code_session.md`: the full Claude Code session (every prompt and Claude's written reply).
- [Add each teammate's saved prompt and response files here.]
