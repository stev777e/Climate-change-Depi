import pandas as pd

df_blue = pd.read_csv('CO2 EMMISIONS BLUE Cleaned.csv')
df_gdp = pd.read_csv('GDP PER COUNTRY Cleaned.csv')
df_pop = pd.read_csv('POPULATION PER COUNTRY Cleaned.csv')
df_capita = pd.read_csv('TOTAL EMISSIONS PER CAPITA Cleaned.csv')
df_total = pd.read_csv('TOTAL EMISSIONS PER COUNTRY Cleaned.csv')
df_gdp_em = pd.read_csv('TOTAL EMISSIONS PER GDP Cleaned.csv')

##################################################################################################################################################

def reshape_df(df, col_name):
    id_vars = [c for c in ['Country', 'Country Code', 'EDGAR Country Code', 'Country Name'] if c in df.columns]
    year_vars = [c for c in df.columns if c.isdigit() or c.replace('.', '', 1).isdigit()]
    melted = df.melt(id_vars=id_vars, value_vars=year_vars, var_name='year', value_name=col_name)
    for c in id_vars:
        if 'Code' in c:
            melted = melted.rename(columns={c: 'iso_code'})
    if 'iso_code' in melted.columns:
        melted['iso_code'] = melted['iso_code'].astype(str).str.strip().str.upper()
    melted['year'] = pd.to_numeric(melted['year'], errors='coerce')
    return melted[['iso_code', 'year', col_name]].dropna(subset=['iso_code', 'year'])

##################################################################################################################################################

df1 = reshape_df(df_total, 'total_ghg_emissions')
df2 = reshape_df(df_blue, 'co2_blue_emissions')
df3 = reshape_df(df_gdp, 'real_gdp')
df4 = reshape_df(df_pop, 'population')
df5 = reshape_df(df_capita, 'ghg_per_capita')
df6 = reshape_df(df_gdp_em, 'ghg_per_gdp')

##################################################################################################################################################

master = df1
for d in [df2, df3, df4, df5, df6]:
    master = pd.merge(master, d, on=['iso_code', 'year'], how='outer')

code_to_name = df_total.set_index('Country Code')['Country'].to_dict()
pop_mapping = df_pop.set_index('Country Code')['Country Name'].to_dict()
code_to_name.update(pop_mapping)

master['country_name'] = master['iso_code'].map(code_to_name)

cols = ['iso_code', 'country_name', 'year'] + [c for c in master.columns if c not in ['iso_code', 'country_name', 'year']]
master = master[cols]

master = master.sort_values(by=['iso_code', 'year']).reset_index(drop=True)
output_filename = 'track_b_country_climate_energy_panel_1970_2025.csv'
master.to_csv(output_filename, index=False)

print("SUCCESS: Merged file created successfully with country names!")