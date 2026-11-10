import re
import sys
import pandas as pd
from decimal import Decimal
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

INPUT_FILE = Path(r"C:\Users\msi\Downloads\1\CO2 EMMISIONS BLUE.csv")
OUTPUT_FILE = Path(r"C:\Users\msi\Downloads\1\Final Project\CO2 EMMISIONS BLUE Cleaned.csv")
# OUTPUT_FILE = INPUT_FILE.with_name("CO2 EMMISIONS BLUE Cleaned.csv")
MAX_EMPTY_RATIO = 0.5

##################################################################################################################################################

country_codes = [
    'AFG', 'ALB', 'DZA', 'AND', 'AGO', 'ATG', 'ARG', 'ARM', 'AUS', 'AUT',
    'AZE', 'BHS', 'BHR', 'BGD', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BTN',
    'BOL', 'BIH', 'BWA', 'BRA', 'BRN', 'BGR', 'BFA', 'BDI', 'KHM', 'CMR',
    'CAN', 'CPV', 'CAF', 'TCD', 'CHL', 'CHN', 'COL', 'COM', 'COG', 'COK',
    'CRI', 'HRV', 'CUB', 'CYP', 'CZE', 'COD', 'DNK', 'DJI', 'DMA', 'DOM',
    'ECU', 'EGY', 'SLV', 'GNQ', 'ERI', 'EST', 'SWZ', 'ETH', 'FJI', 'FIN',
    'FRA', 'GAB', 'GMB', 'GEO', 'DEU', 'GHA', 'GRC', 'GRD', 'GTM', 'GIN',
    'GNB', 'GUY', 'HTI', 'HND', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'IRQ',
    'IRL', 'ISR', 'ITA', 'CIV', 'JAM', 'JPN', 'JOR', 'KAZ', 'KEN', 'KIR',
    'KWT', 'KGZ', 'LAO', 'LVA', 'LBN', 'LSO', 'LBR', 'LBY', 'LIE', 'LTU',
    'LUX', 'MDG', 'MWI', 'MYS', 'MDV', 'MLI', 'MLT', 'MHL', 'MRT', 'MUS',
    'MEX', 'FSM', 'MDA', 'MCO', 'MNG', 'MNE', 'MAR', 'MOZ', 'MMR', 'NAM',
    'NRU', 'NPL', 'NLD', 'NZL', 'NIC', 'NER', 'NGA', 'NIU', 'PRK', 'MKD',
    'NOR', 'OMN', 'PAK', 'PLW', 'PSE', 'PAN', 'PNG', 'PRY', 'PER', 'PHL',
    'POL', 'PRT', 'QAT', 'ROU', 'RUS', 'RWA', 'KNA', 'LCA', 'VCT', 'WSM',
    'SMR', 'STP', 'SAU', 'SEN', 'SRB', 'SYC', 'SLE', 'SGP', 'SVK', 'SVN',
    'SLB', 'SOM', 'ZAF', 'KOR', 'SSD', 'ESP', 'LKA', 'SDN', 'SUR', 'SWE',
    'CHE', 'SYR', 'TJK', 'THA', 'TLS', 'TGO', 'TON', 'TTO', 'TUN', 'TUR',
    'TKM', 'TUV', 'UGA', 'UKR', 'ARE', 'GBR', 'TZA', 'USA', 'URY', 'UZB',
    'VUT', 'VAT', 'VEN', 'VNM', 'YEM', 'ZMB', 'ZWE',
]
country_codes += [None, None, None, None]

##################################################################################################################################################

raw = pd.read_csv(
    INPUT_FILE, sep=None, engine="python",
    dtype=str, keep_default_na=False, encoding="utf-8-sig",
)

##################################################################################################################################################

first = raw.columns[0]
unit = first.replace("unit:", "").strip()
print(f"Unit: {unit}")

df = raw.set_index(first).T
df.index.name = "Country"
df = df.reset_index()
df.columns = df.columns.astype(str)

assert len(country_codes) == len(df), (len(country_codes), len(df))
df.insert(1, "Country Code", country_codes)

year_cols = list(df.columns[2:])

NUMBER_RE = re.compile(r"[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?")


def clean_cell(value):
    s = str(value).strip()
    if not NUMBER_RE.fullmatch(s):
        return None
    if "e" in s.lower():
        s = format(Decimal(s), "f")
        if "." in s:
            s = s.rstrip("0").rstrip(".")
    return s


df[year_cols] = df[year_cols].apply(lambda col: col.map(clean_cell))

empty_ratio = df[year_cols].isna().mean(axis=1)
df = df[empty_ratio <= MAX_EMPTY_RATIO].reset_index(drop=True)

df.to_csv(OUTPUT_FILE, index=False, na_rep="null", encoding="utf-8-sig")
print(f"Saved to: {OUTPUT_FILE}")

df[year_cols] = df[year_cols].astype(float)
df.columns = list(df.columns[:2]) + [int(c) for c in year_cols]

print(df.dtypes.value_counts())
print(f"Rows after cleaning: {len(df)}")