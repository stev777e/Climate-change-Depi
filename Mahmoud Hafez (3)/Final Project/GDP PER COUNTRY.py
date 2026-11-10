import numpy as np
import pandas as pd

pd.set_option("display.max_columns", None)

df = pd.read_csv(
    r"C:\Users\msi\Downloads\1\GDP PER COUNTRY.csv",
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False,
)

##################################################################################################################################################

df.drop(columns=["Indicator Name", "Indicator Code"], inplace=True)

year_cols = df.columns[2:]

##################################################################################################################################################

for col in year_cols:
    df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce")

df[year_cols] = df[year_cols].replace([np.inf, -np.inf], np.nan).astype("float64")

df = df.dropna(subset=year_cols, how="all").reset_index(drop=True)

##################################################################################################################################################

df.to_csv(
    "GDP PER COUNTRY Cleaned.csv",
    index=False,
    float_format="%.1f",
    na_rep="null",
    encoding="utf-8-sig",
)

print(df.shape)
print(df[year_cols].dtypes.unique())