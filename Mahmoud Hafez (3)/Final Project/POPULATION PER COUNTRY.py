import numpy as np
import pandas as pd

pd.set_option('display.max_columns', None)

def clean_numeric_df(df, id_cols):
    num_cols = [c for c in df.columns if c not in id_cols]
    for c in num_cols:
        df[c] = pd.to_numeric(df[c].astype(str).str.strip(), errors="coerce").astype("float64")
    df = df.dropna(subset=num_cols, how="all").reset_index(drop=True)
    return df, num_cols

##################################################################################################################################################

def save_clean_csv(df, num_cols, path):
    out = df.copy()
    for c in num_cols:
        out[c] = out[c].map(
            lambda v: np.format_float_positional(v, trim="0") if pd.notna(v) else "null"
        )
    out.to_csv(path, index=False, encoding="utf-8-sig")

##################################################################################################################################################

df = pd.read_csv(
    r"C:\Users\msi\Downloads\1\POPULATION PER COUNTRY.csv",
    dtype=str,
    encoding="utf-8-sig",
)

df.drop(columns=['Indicator Name', 'Indicator Code'], inplace=True)

df, num_cols = clean_numeric_df(df, id_cols=['Country Name', 'Country Code'])
save_clean_csv(df, num_cols, "POPULATION PER COUNTRY Cleaned.csv")