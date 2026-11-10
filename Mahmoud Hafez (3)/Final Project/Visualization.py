import sys, os
sys.stdout.reconfigure(encoding="utf-8")
sys.stderr.reconfigure(encoding="utf-8")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

CSV = sys.argv[1] if len(sys.argv) > 1 else "track_b_country_climate_energy_panel_1970_2025.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "outputs"
os.makedirs(OUT, exist_ok=True)

Y0, Y1 = 2005, 2025
LULUCF_COLS = [c for c in ["co2_blue_emissions", "co2_oscar_emissions", "co2_luce_emissions"]]

df = pd.read_csv(CSV)
df = df[df["year"].between(1970, 2025)].copy()

AGGREGATES = {"AIR", "SEA", "EU27", "GLOBAL TOTAL", "ANT", "SCG", "ESH"}
df = df[df["iso_code"].str.fullmatch(r"[A-Z]{3}") & ~df["iso_code"].isin(AGGREGATES)]
df["country_name"] = df.groupby("iso_code")["country_name"].transform(lambda s: s.ffill().bfill())
df["country_name"] = df["country_name"].fillna(df["iso_code"])

df["ghg_per_capita"] = df["total_ghg_emissions"] / df["population"]
df["ghg_per_capita"] *= 1e6
df["ghg_per_gdp"]    = df["total_ghg_emissions"] * 1e6 / df["real_gdp"]
df["gdp_per_capita"] = df["real_gdp"] / df["population"]
df.to_csv(f"{OUT}/panel_with_indicators.csv", index=False)

last = df[(df.year == 2023)].dropna(subset=["total_ghg_emissions", "real_gdp", "population"])
corr = pd.DataFrame({
    "pearson_raw": last[["total_ghg_emissions", "real_gdp", "population"]].corr().iloc[0, 1:],
    "pearson_log": np.log(last[["total_ghg_emissions", "real_gdp", "population"]]).corr().iloc[0, 1:],
    "spearman":    last[["total_ghg_emissions", "real_gdp", "population"]].corr("spearman").iloc[0, 1:],
})
print("\n[1] الارتباط مع إجمالي الانبعاثات (2023):\n", corr.round(3))
corr.to_csv(f"{OUT}/q1_correlations.csv")

rank = last[["iso_code", "country_name", "total_ghg_emissions", "ghg_per_capita"]].copy()
rank["rank_total"] = rank.total_ghg_emissions.rank(ascending=False).astype(int)
rank["rank_per_capita"] = rank.ghg_per_capita.rank(ascending=False).astype(int)
rank["rank_shift"] = rank.rank_total - rank.rank_per_capita
rank.sort_values("rank_total").to_csv(f"{OUT}/q1_rankings_2023.csv", index=False)
print("أعلى 10 إجمالًا:\n", rank.nsmallest(10, "rank_total")[["country_name", "rank_total", "rank_per_capita"]].to_string(index=False))
print("أعلى 10 للفرد:\n", rank.nsmallest(10, "rank_per_capita")[["country_name", "rank_total", "rank_per_capita"]].to_string(index=False))

a = df[df.year == Y0].set_index("iso_code"); b = df[df.year == Y1].set_index("iso_code")
dec = pd.DataFrame({
    "country_name": b["country_name"],
    "gdp_growth_pct": (b.real_gdp / a.real_gdp - 1) * 100,
    "ghg_change_pct": (b.total_ghg_emissions / a.total_ghg_emissions - 1) * 100,
    "population": b.population,
    "gdp_pc_2025": b.gdp_per_capita,
}).dropna(subset=["gdp_growth_pct", "ghg_change_pct"])
dec["absolute_decoupling"] = (dec.gdp_growth_pct > 0) & (dec.ghg_change_pct < 0)

if "income_group" in df.columns:
    dec["income_group"] = df.dropna(subset=["income_group"]).groupby("iso_code")["income_group"].last()
else:
    bins = [0, 1_200, 4_500, 14_000, np.inf]
    dec["income_group"] = pd.cut(dec.gdp_pc_2025, bins,
                                 labels=["Low", "Lower-middle", "Upper-middle", "High"]).astype(object)
    dec["income_group"] = dec["income_group"].fillna("Unknown")
dec.to_csv(f"{OUT}/q2_decoupling_{Y0}_{Y1}.csv")
n_dec = int(dec.absolute_decoupling.sum())
print(f"\n[2] عدد الدول ذات الـ Absolute Decoupling ({Y0}-{Y1}): {n_dec} من {len(dec)}")
print(dec[dec.absolute_decoupling].sort_values("ghg_change_pct")[["country_name", "gdp_growth_pct", "ghg_change_pct"]].head(15).round(1).to_string())

colors = {"Low": "#d62728", "Lower-middle": "#ff7f0e", "Upper-middle": "#2ca02c", "High": "#1f77b4", "Unknown": "#999999"}
fig, ax = plt.subplots(figsize=(11, 8))
for g, s in dec.groupby("income_group"):
    ax.scatter(s.gdp_growth_pct, s.ghg_change_pct, s=40, alpha=.75, c=colors.get(g, "#999"), label=g, edgecolor="white", lw=.4)
ax.axhline(0, c="k", lw=.8); ax.axvline(0, c="k", lw=.8)
ax.axhspan(ax.get_ylim()[0], 0, xmin=0.5, alpha=.04, color="green")
q4 = dec[dec.absolute_decoupling]
for iso, r in q4.nlargest(12, "gdp_growth_pct").iterrows():
    ax.annotate(r.country_name, (r.gdp_growth_pct, r.ghg_change_pct), fontsize=7, xytext=(3, 3), textcoords="offset points")
ax.set_xscale("symlog", linthresh=100); ax.set_yscale("symlog", linthresh=100)
ax.set_xlabel(f"GDP change {Y0}–{Y1} (%)"); ax.set_ylabel(f"GHG change {Y0}–{Y1} (%)")
ax.set_title(f"Four-quadrant decoupling – {n_dec} countries in Q-IV (GDP↑, GHG↓)")
ax.legend(title="Income group (proxy)" if "income_group" not in df.columns else "Income group")
plt.tight_layout(); plt.savefig(f"{OUT}/fig1_decoupling_quadrants.png", dpi=200); plt.close()

e = df[df.year == Y1].dropna(subset=["gdp_per_capita", "ghg_per_capita", "population"])
e = e[(e.gdp_per_capita > 0) & (e.ghg_per_capita > 0)]
fig, ax = plt.subplots(figsize=(11, 8))
sc = ax.scatter(e.gdp_per_capita, e.ghg_per_capita, s=e.population / e.population.max() * 3000 + 8,
                c=np.log10(e.gdp_per_capita), cmap="viridis", alpha=.6, edgecolor="k", lw=.3)
ax.set_xscale("log"); ax.set_yscale("log")
x, y = np.log10(e.gdp_per_capita), np.log10(e.ghg_per_capita)
c2, c1, c0 = np.polyfit(x, y, 2); xs = np.linspace(x.min(), x.max(), 200)
ax.plot(10 ** xs, 10 ** (c2 * xs ** 2 + c1 * xs + c0), "r--", lw=1.5, label="Quadratic log-log fit")
for iso in ["USA", "CHN", "IND", "DEU", "BRA", "RUS", "QAT", "EGY", "NGA"]:
    r = e[e.iso_code == iso]
    if len(r): ax.annotate(r.country_name.iloc[0], (r.gdp_per_capita.iloc[0], r.ghg_per_capita.iloc[0]), fontsize=8)
ax.set_xlabel("GDP per capita (log)"); ax.set_ylabel("GHG per capita, tCO2e (log)")
ax.set_title(f"Environmental Kuznets Curve ({Y1}) – bubble size = population"); ax.legend()
plt.tight_layout(); plt.savefig(f"{OUT}/fig2_ekc_loglog.png", dpi=200); plt.close()

cols = [c for c in LULUCF_COLS if c in df.columns]
last_y = int(df.loc[df[cols[0]].notna(), "year"].max())
win = df[df.year.between(last_y - 9, last_y)]
g = win.groupby("iso_code")
lu = pd.DataFrame({"country_name": g["country_name"].last(), "population": g["population"].last()})
if len(cols) > 1:
    per_model = pd.concat({c: g[c].mean() for c in cols}, axis=1)
    lu["mean"], lu["lo"], lu["hi"] = per_model.mean(1), per_model.min(1), per_model.max(1)
    rng_label = "model range"
else:
    lu["mean"], lu["lo"], lu["hi"] = g[cols[0]].mean(), g[cols[0]].min(), g[cols[0]].max()
    rng_label = f"year-to-year range {last_y-9}–{last_y}"
lu = lu.dropna(subset=["mean"])
lu["class"] = np.where(lu["mean"] < 0, "Net sink", "Net emitter")
lu.to_csv(f"{OUT}/q3_lulucf_classification.csv")
print(f"\n[3] LULUCF ({last_y-9}-{last_y}): بالوعات صافية={int((lu['class']=='Net sink').sum())} | مصادر صافية={int((lu['class']=='Net emitter').sum())}")
print("أكبر البالوعات:", lu.nsmallest(5, "mean").country_name.tolist())
print("أكبر المصادر :", lu.nlargest(5, "mean").country_name.tolist())

top = pd.concat([lu.nsmallest(15, "mean"), lu.nlargest(15, "mean")]).sort_values("mean")
fig, ax = plt.subplots(figsize=(10, 9))
yy = np.arange(len(top))
ax.barh(yy, top["mean"], color=np.where(top["mean"] < 0, "#2e8b57", "#b22222"), alpha=.8)
ax.errorbar(top["mean"], yy, xerr=[top["mean"] - top.lo, top.hi - top["mean"]], fmt="none", ecolor="k", capsize=3, lw=1)
ax.set_yticks(yy); ax.set_yticklabels(top.country_name, fontsize=8); ax.axvline(0, c="k", lw=.8)
ax.set_xlabel("Land-use CO2 (Mt/yr)  –  negative = carbon sink")
ax.set_title(f"LULUCF emissions: top sinks vs. top emitters ({rng_label})")
plt.tight_layout(); plt.savefig(f"{OUT}/fig3_lulucf_sinks.png", dpi=200); plt.close()
print(f"\nتم الحفظ في: {os.path.abspath(OUT)}")