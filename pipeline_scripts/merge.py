from clean import nmc_clean, alliance_df, natl_trade, dyadic_war_df, country_codes
import pandas as pd


nmc_data = nmc_clean
alliance_data = alliance_df
trade_data = natl_trade
war_data = dyadic_war_df
country_codes_data = country_codes

def merge_nmc_country_codes(nmc, country_codes):

    nmc = pd.merge(nmc, country_codes, on='ccode')

    return nmc

def merge_nmc_war_trade_alliance(nmc, war, trade, alliance):

    nmc_war = pd.merge(nmc, war, on=['ccode', 'year'], how='outer')
    nmc_war_trade = pd.merge(left=nmc_war, right=natl_trade, left_on=['ccode', 'year'],
                             right_on=['ccode', 'year'], how='left')
    nmc_war_trade_alliance = pd.merge(left=nmc_war_trade, right=alliance_df, left_on=['ccode',
                                      'year'], right_on=['ccode', 'year'], how='left')

    nmc_war_trade_alliance = nmc_war_trade_alliance[['StateNme', 'ccode', 'year', 'irst', 'milex', 'milper', 'pec', 'tpop',
       'upop', 'cinc', 'warnum', 'outcomea', 'batdtha', 'batdths',
       'imports', 'exports', 'surplus', 'expt_past_yr', 'expt_past_5_yrs',
       'impt_past_yr', 'impt_past_5_yrs', 'ccode2', 'left_censor',
       'right_censor', 'defense', 'neutrality', 'nonaggression', 'entente']]

    return nmc_war_trade_alliance



nmc_war_trade_alliance = merge_nmc_war_trade_alliance(merge_nmc_country_codes(nmc_data, country_codes_data), war_data, trade_data, alliance_data)