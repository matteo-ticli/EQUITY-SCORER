import requests
import pandas as pd
import json
import matplotlib.pyplot as plt
import datetime as dt
import re
import time

# This is the key to connect to Financial Modeling Prep API
api_key = "34cf2bfdc6e362cdf373bc84d1b4b227"


def Piotroski_fscore(api_key, ticker):
    f_score = 0

    # Download Balance Sheet
    balance_sheet = requests.get(
        "https://financialmodelingprep.com/api/v3/balance-sheet-statement/" + ticker + "?limit=120&apikey=" + api_key)
    balance_sheet = balance_sheet.json()

    # Download Income statement
    income_statement = requests.get(
        "https://financialmodelingprep.com/api/v3/income-statement/" + ticker + "?limit=120&apikey=" + api_key)
    income_statement = income_statement.json()

    # Download Financial Ratios
    fin_ratios = requests.get(
        "https://financialmodelingprep.com/api/v3/ratios/" + ticker + "?limit=40&apikey=" + api_key)
    fin_ratios = fin_ratios.json()

    # Download Financial Ratios TTM
    fin_ratios_ttm = requests.get(
        "https://financialmodelingprep.com/api/v3/ratios-ttm/" + ticker + "?apikey=" + api_key)
    fin_ratios_ttm = fin_ratios_ttm.json()

    # Download Cash Flow Statement
    cash_flow = requests.get(
        "https://financialmodelingprep.com/api/v3/cash-flow-statement/" + ticker + "?limit=120&apikey=" + api_key)
    cash_flow = cash_flow.json()

    # get data
    bs_last_y = balance_sheet[0]
    bs_prev_y = balance_sheet[1]
    is_last_y = income_statement[0]
    fr_last_y = fin_ratios[0]
    fr_prev_y = fin_ratios[1]
    cf_last_y = cash_flow[0]

    # Select ttm data
    fr_ttm = fin_ratios_ttm[0]

    # PROFITAVBILITY CRITERIA

    #  ROA
    if fr_ttm['returnOnAssetsTTM'] > 0:
        f_score += 1

    # Operating Cash Flow
    if cf_last_y['operatingCashFlow'] > 0:
        f_score += 1

    # Delta ROA
    if (fr_last_y['returnOnAssets'] > fr_prev_y['returnOnAssets']):
        f_score += 1

    # Accrual
    if (cf_last_y['operatingCashFlow'] / bs_last_y['totalAssets']) > fr_ttm['returnOnAssetsTTM']:
        f_score += 1

    # LEVERAGE CRITERIA

    # Delta Long Term Debt
    if (bs_last_y['longTermDebt'] < bs_prev_y['longTermDebt']):
        f_score += 1

    # Delta Current Ratio
    if fr_last_y['currentRatio'] > fr_prev_y['currentRatio']:
        f_score += 1

    # Delta Common Equity
    if bs_last_y['totalStockholdersEquity'] > bs_prev_y['totalStockholdersEquity']:
        f_score += 1

    # OPERATING EFFICIENCY

    # Delta Gross Margin Ratio
    if fr_last_y['grossProfitMargin'] > fr_prev_y['grossProfitMargin']:
        f_score += 1

    # Delta Turnover Ratio
    if fr_last_y['assetTurnover'] > fr_prev_y['assetTurnover']:
        f_score += 1

    return f_score


def Piotroski_fscore_new(api_key, ticker):
    f_score = 0

    # Download Balance Sheet
    balance_sheet = requests.get(
        "https://financialmodelingprep.com/api/v3/balance-sheet-statement/" + ticker + "?limit=120&apikey=" + api_key)
    balance_sheet = balance_sheet.json()

    # Download Income statement
    income_statement = requests.get(
        "https://financialmodelingprep.com/api/v3/income-statement/" + ticker + "?limit=120&apikey=" + api_key)
    income_statement = income_statement.json()

    # Download Financial Ratios
    fin_ratios = requests.get(
        "https://financialmodelingprep.com/api/v3/ratios/" + ticker + "?limit=120&apikey=" + api_key)
    fin_ratios = fin_ratios.json()

    # Download Cash Flow Statement
    cash_flow = requests.get(
        "https://financialmodelingprep.com/api/v3/cash-flow-statement/" + ticker + "?limit=120&apikey=" + api_key)
    cash_flow = cash_flow.json()

    # Download Cash Flow Statement as Reported
    cash_flow_reported = requests.get(
        "https://financialmodelingprep.com/api/v3/cash-flow-statement-as-reported/" + ticker + "?limit=120&apikey=" + api_key)
    cash_flow_reported = cash_flow_reported.json()

    # Download Financial Ratios TTM
    fin_ratios_ttm = requests.get(
        "https://financialmodelingprep.com/api/v3/ratios-ttm/" + ticker + "?limit=120&apikey=" + api_key)
    fin_ratios_ttm = fin_ratios_ttm.json()

    # Get data (t: the last statement, t1: is t-1, t2: is t-2)
    bs_t = balance_sheet[0]
    bs_t1 = balance_sheet[1]
    bs_t2 = balance_sheet[2]

    is_t = income_statement[0]
    is_t1 = income_statement[1]

    fr_t = fin_ratios[0]
    fr_t1 = fin_ratios[1]

    cf_t = cash_flow[0]
    cf_t1 = cash_flow[1]

    cfr_t = cash_flow_reported[0]

    fr_ttm_t = fin_ratios_ttm[0]

    # Current profitability

    # ROA
    if fr_t['returnOnAssets'] > 0:
        f_score += 1

    # FCFTA
    if (cf_t['freeCashFlow'] / bs_t['totalAssets']) > 0:
        f_score += 1

    # ACCRUAL
    if (cf_t['freeCashFlow'] / bs_t['totalAssets']) > fr_ttm_t['returnOnAssetsTTM']:
        f_score += 1

    # Stability

    # DELTA LEVERAGE
    if (bs_t['longTermDebt'] / bs_t['totalAssets']) < (bs_t1['longTermDebt'] / bs_t1['totalAssets']):
        f_score += 1

    # DELTA LIQUIDITY
    if (bs_t['totalCurrentAssets'] / bs_t['totalCurrentLiabilities']) > (
            bs_t1['totalCurrentAssets'] / bs_t1['totalCurrentLiabilities']):
        f_score += 1

    # NEQISS
    try:
        if cfr_t['paymentsforrepurchaseofcommonstock'] - cfr_t['proceedsfromissuanceofcommonstock'] > 0:
            f_score += 1
    except:
        f_score += 0

    # Recent Operational Improvements

    # DELTA ROA
    if fr_t['returnOnAssets'] - fr_t1['returnOnAssets'] > 0:
        f_score += 1

    # DELTA FCFTA
    if (cf_t['freeCashFlow'] / bs_t['totalAssets']) - (cf_t1['freeCashFlow'] / bs_t1['totalAssets']) > 0:
        f_score += 1

    # DELTA MARGIN
    if ((is_t['revenue'] - is_t['costOfRevenue']) / is_t['revenue']) - (
            (is_t1['revenue'] - is_t1['costOfRevenue']) / is_t1['revenue']) > 0:
        f_score += 1

    # DELTA TURNOVER
    if (is_t['revenue'] / bs_t1['totalAssets']) - (is_t1['revenue'] / bs_t2['totalAssets']) > 0:
        f_score += 1

    return f_score


def calculate_score(companies, mode=True):
    scores = dict()
    for ticker in companies:
        if not mode:
            score = Piotroski_fscore(api_key, ticker)
            scores[ticker] = score
            time.sleep(1.5)
        else:
            score = Piotroski_fscore_new(api_key, ticker)
            scores[ticker] = score
            time.sleep(1.5)

    return scores

companies = ['AAPL','MSFT','AMZN','FB','TSLA','WMT','BA','JNJ','SYF','BRKB','GOOGL','NFLX','IVR']

scores = calculate_score(companies)
print(scores)