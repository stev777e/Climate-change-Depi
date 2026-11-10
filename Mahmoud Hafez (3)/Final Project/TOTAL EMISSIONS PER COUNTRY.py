import numpy as np
import pandas as pd
from decimal import Decimal

INPUT_FILE = r"C:\Users\msi\Downloads\1\TOTAL EMISSIONS PER COUNTRY.csv"
OUTPUT_FILE = "TOTAL EMISSIONS PER COUNTRY Cleaned.csv"

pd.set_option('display.max_columns', None)

df = pd.read_csv(
    INPUT_FILE,
    dtype=str,
    encoding="utf-8-sig",
    keep_default_na=False
)

##################################################################################################################################################

df.columns = df.columns.str.strip()

df.rename(columns={'EDGAR Country Code': 'Country Code'}, inplace=True)
df = df[['Country', 'Country Code'] + [col for col in df.columns if col not in ['Country', 'Country Code']]]

year_cols = [c for c in df.columns if c.isdigit()]

for col in year_cols:
    df[col] = pd.to_numeric(df[col].str.strip(), errors="coerce").astype("float64")

df[year_cols] = df[year_cols].replace([np.inf, -np.inf], np.nan)

df = df.dropna(subset=year_cols, how="all").reset_index(drop=True)

def to_plain(x):
    if pd.isna(x):
        return ""
    s = format(Decimal(repr(float(x))), "f")
    return s if "." in s else s + ".0"

out = df.copy()
for col in year_cols:
    out[col] = df[col].map(to_plain)
    
##################################################################################################################################################

out.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")

check = pd.read_csv(OUTPUT_FILE)
print(check.shape)
print(check[year_cols].dtypes.unique())