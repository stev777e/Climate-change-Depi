import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)

INPUT  = r"C:\Users\msi\Downloads\1\TOTAL EMISSIONS PER GDP.csv"
OUTPUT = r"C:\Users\msi\Downloads\1\Final Project\TOTAL EMISSIONS PER GDP Cleaned.csv"

df = pd.read_csv(INPUT, dtype=str, keep_default_na=False, encoding="utf-8-sig")

##################################################################################################################################################

df.rename(columns={"EDGAR Country Code": "Country Code"}, inplace=True)
df = df[
    ["Country", "Country Code"]
    + [col for col in df.columns if col not in ["Country", "Country Code"]]
]

value_cols = [c for c in df.columns if c not in ["Country", "Country Code"]]

for col in value_cols:
    df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce").astype("float64")

df[value_cols] = df[value_cols].replace([np.inf, -np.inf], np.nan)

before = len(df)
df = df.dropna(subset=value_cols, how="all").reset_index(drop=True)
print(f"Removed {before - len(df)} rows, {len(df)} rows remaining")

##################################################################################################################################################

df.to_csv(
    OUTPUT,
    index=False,
    encoding="utf-8-sig",
    float_format=lambda x: np.format_float_positional(x, trim="-"),
)

print(df[value_cols].dtypes.unique())