import pandas as pd
import requests

census = {
    'tot_pop': 'DP05_0033E',
    'elderly_pop': 'DP05_0024E',
    'male_pop': 'DP05_0002E',
    'female_pop': 'DP05_0003E',
    'white_pop': 'DP05_0064E',
    'black_pop': 'DP05_0065E',
    'native_american_pop': 'DP05_0066E',
    'asian_pop': 'DP05_0067E',
    'two_or_more_pop': 'DP05_0058E',
    'hispanic_pop': 'DP05_0071E',
    'adult_pop': 'DP05_0021E',
    'citizen_adult_pop': 'DP05_0087E',
    'avg_household_size': 'DP02_0016E',
    'pop_under_5_years': 'DP05_0005E',
    'pop_5_to_9_years': 'DP05_0006E',
    'pop_10_to_14_years': 'DP05_0007E',
    'pop_15_to_19_years': 'DP05_0008E',
    'pop_20_to_24_years': 'DP05_0009E',
    'pop_25_to_34_years': 'DP05_0010E',
    'pop_35_to_44_years': 'DP05_0011E',
    'pop_45_to_54_years': 'DP05_0012E',
    'pop_55_to_59_years': 'DP05_0013E',
    'pop_60_to_64_years': 'DP05_0014E',
    'pop_65_to_74_years': 'DP05_0015E',
    'pop_75_to_84_years': 'DP05_0016E',
    'pop_85_years_and_over': 'DP05_0017E',
    'per_capita_income': 'DP03_0088E',
    'median_income_for_workers': 'DP03_0092E',
}


CENSUS_URL = f"https://api.census.gov/data/2021/acs/acs5/profile?get=NAME,{','.join(census.values())}&for=zip%20code%20tabulation%20area:*"

def header_from_first_row(df):
    new_header = df.iloc[0]
    df = df[1:]
    df.columns = new_header
    return df


census_df = header_from_first_row(pd.read_json(CENSUS_URL))
display(census_df.head())
inv_map = {census[k] : k for k in census}
census_df = census_df.rename(columns=inv_map)


def fmt(c: str):
    return c.replace(' ', '_').lower()

census_df.columns = [fmt(x) for x in census_df.columns]
census_df = census_df.rename(
  columns={
      'zip_code_tabulation_area': 'zip_code'
  }
)
census_df.head()
census_df.drop(['name'], axis=1, inplace=True)
for col in census_df.columns:
    if col not in ('zip_code'):
        census_df[col] = census_df[col].astype(float)
