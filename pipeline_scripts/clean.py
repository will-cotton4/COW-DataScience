import numpy as np
import pandas as pd


URLS = {"NMC_URL": "https://raw.githubusercontent.com/NicoMontoya/COW-DataScience/master/data/NMC_v4_0.csv",
        "DYADIC_WAR_URL": "https://raw.githubusercontent.com/NicoMontoya/COW-DataScience/master/data/directed_dyadic_war.csv",
        "COUNTRY_CODES_URL": "https://raw.githubusercontent.com/NicoMontoya/COW-DataScience/master/data/COW%20country%20codes.csv",
        "TRADE_URL": "https://raw.githubusercontent.com/NicoMontoya/COW-DataScience/master/data/National_COW_4.0.csv",
        "ALLIANCE_URL": "https://raw.githubusercontent.com/beverast/COW-DataScience/master/data/engineered_dyads_yearly.csv",
        "COUNTRIES_JSON_URL": "https://raw.githubusercontent.com/will-cotton4/COW-DataScience/master/countries.json",}

# READ NMC "Material" DATA
nmc_df = pd.read_csv(URLS["NMC_URL"])

# IMPUTE NMC NaNs
df_ff = nmc_df.fillna(method='bfill')
df_ff.iloc[10569:10570][['tpop', 'upop']] = df_ff.iloc[10568:10569][['tpop', 'upop']]
nmc_clean = df_ff.fillna(method='ffill').drop(columns='stateabb')

# READ DYADIC WAR DATA
dyadic_cols_to_keep = ['statea', 'warnum', 'year', 'outcomea', 'batdtha', 'batdths']
dyadic_war_df = pd.read_csv(URLS["DYADIC_WAR_URL"], usecols=dyadic_cols_to_keep)
dyadic_war_df = dyadic_war_df.rename(columns={'statea': 'ccode'})

# READ COUNTRY CODES
country_cols_to_keep = ['CCode', 'StateNme']
country_codes = pd.read_csv(URLS["COUNTRY_CODES_URL"], usecols=country_cols_to_keep)
country_codes = country_codes.rename(columns={'CCode':'ccode'})


def leak_fix_shift(df, cols, state_col):
    # Fixes leaky data by shifting information back a year so the previous
    # year's data can be used for prediction.
    df = df.copy()
    states = df[state_col].value_counts().keys()
    for col in cols:
        for state in states:
            df[df[state_col]==state][col] = df[df[state_col]==state][col].shift(periods=1)
    return df


def clean_natl_trade(df):
    # This method cleans the national trade dataset:
    # - Removes alt_imports and alt_exports; these were specially designated for
    #   Belgium and Luxembourg (who have a special economic relationsip) and China
    #   (due to the special status of Macao and Hong Kong)
    # - Removes version, source1, and source2 (reporting variables, unrelated to 
    #   status of country)
    # - Use forward fill for each country missing import/export data, then back
    #   fill to capture missing data. The remaining rows are dropped, because
    #   they correspond to countries with no import/export data at all.
    # - Standardize imports, exports (commented out)
    # - Shift data back a year to fix leaks (commented out)
    # - Add trade deficit feature
    # - Add increase/decrease in imports/exports from past year/past 5 years

    df = df.copy()

    df = df.drop(columns=['alt_imports', 'alt_exports', 
                        'source1', 'source2', 'version'])
    inc_cond = df['imports'].isnull()
    incomplete = df[inc_cond]['statename'].value_counts().keys()

    for state in incomplete:
        state_cond = df['statename'] == state
        df[state_cond] = df[state_cond].ffill(axis=0)
        df[state_cond] = df[state_cond].bfill(axis=0)

    df = df.dropna()

    # Shift data to fix leaks
    leaks = ['imports', 'exports']
    df = leak_fix_shift(df, leaks, 'statename')

    # Add surplus column
    df['surplus'] = df['exports'] - df['imports']

    # Add columns measuring change in exports/imports over one/five years
    df['expt_past_yr'] = df['exports'] - df['exports'].shift(periods=1)
    df['expt_past_5_yrs'] = df['exports'] - df['exports'].shift(periods=5)

    df['impt_past_yr'] = df['imports'] - df['imports'].shift(periods=1)
    df['impt_past_5_yrs'] = df['imports'] - df['imports'].shift(periods=5)
    df = df.bfill()

    return df


# READ AND CLEAN TRADE DATA
trade_df = pd.read_csv(URLS["TRADE_URL"])
natl_trade = clean_natl_trade(trade_df)
natl_trade = natl_trade.drop(columns=['statename'])


# READ AND CLEAN ALLIANCE DATA
alliance_cols_to_keep = ['ccode1', 'year', 'ccode2', 'left_censor', 'right_censor', 'defense', 'neutrality', 'nonaggression', 'entente']
alliance_df = pd.read_csv(URLS["ALLIANCE_URL"], usecols=alliance_cols_to_keep)
alliance_df = alliance_df.rename(columns={'ccode1': 'ccode'})


# READ AND CLEAN countries.json
countries_json = pd.read_json(URLS["COUNTRIES_JSON_URL"])
countries_json = countries_json.rename(columns={'name':'StateNme'})
countries_dict = {'United States': 'United States of America',
                  'Saint Vincent and the Grenadines':'St. Vincent and the Grenadines',
                  'Antigua and Barbuda': 'Antigua & Barbuda',
                  'Macedonia [FYROM]': 'Macedonia',
                  'São Tomé and Príncipe': 'Sao Tome and Principe',
                  "Côte d'Ivoire": 'Ivory Coast',
                  'Congo [Republic]': 'Congo',
                  'Congo [DRC]': 'Democratic Republic of the Congo',
                  'Myanmar [Burma]': 'Myanmar',
                  'Timor-Leste': 'East Timor',
                  'Micronesia': 'Federated States of Micronesia'}
countries_json = countries_json.replace(countries_dict)
