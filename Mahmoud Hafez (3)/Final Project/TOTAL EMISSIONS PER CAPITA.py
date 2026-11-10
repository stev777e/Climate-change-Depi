import numpy as np
import pandas as pd

df = pd.read_csv(
    r"C:\Users\msi\Downloads\1\TOTAL EMISSIONS PER CAPITA.csv",
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False,
)

##################################################################################################################################################

year_cols = df.columns[2:]

for col in year_cols:
    df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce")

df[year_cols] = df[year_cols].replace([np.inf, -np.inf], np.nan).astype("float64")

df = df.dropna(subset=year_cols, how="all").reset_index(drop=True)

##################################################################################################################################################

out = df.copy()
out[year_cols] = out[year_cols].apply(
    lambda col: col.map(
        lambda x: np.format_float_positional(x, trim="0") if pd.notna(x) else "null"
    )
)
out.to_csv(
    "TOTAL EMISSIONS PER CAPITA Cleaned.csv",
    index=False,
    encoding="utf-8-sig",
)

print(df.shape)
print(df[year_cols].dtypes.unique())