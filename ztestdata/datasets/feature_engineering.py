##
## Copyright 2024 Zest AI All Rights Reserved
##
##
##
## It is prohibited to copy, in whole or in part, modify, directly or indirectly reverse engineer, disassemble, decompile, decode or adapt this code or any portion or aspect thereof, or otherwise attempt to derive or gain access to any part of the source code or algorithms contained herein as provided in your ZAML agreement.
##
"""Feature engineering for 2007-2012 lendingclub dataset
"""
from functools import reduce
from collections import OrderedDict
import numpy as np
import pandas as pd


# dict of vars to keep and their data dictionary description
GOOD_VAR = OrderedDict([
    ('loan_status', 'the target'),
    ('loan_amnt', 'The listed amount of the loan applied for by the borrower. If at some point in time, the credit department reduces the loan amount, then it will be reflected in this value.'),
    ('term', 'The number of payments on the loan. Values are in months and can be either 36 or 60.'),
    ('int_rate', 'Interest Rate on the loan'),
    ('installment', 'The monthly payment owed by the borrower if the loan originates.'),
    ('emp_length', 'Employment length in years. Possible values are between 0 and 10 where 0 means less than one year and 10 means ten or more years. '),
    ('home_ownership', 'The home ownership status provided by the borrower during registration or obtained from the credit report. Our values are: RENT, OWN, MORTGAGE, OTHER'),
    ('annual_inc', 'The self-reported annual income provided by the borrower during registration.'),
    ('verification_status', 'Indicates if income was verified by LC, not verified, or if the income source was verified'),
    ('issue_d', 'The month which the loan was funded'),
    ('purpose', 'A category provided by the borrower for the loan request. '),
    ('addr_state', 'The state provided by the borrower in the loan application'),
    ('dti', 'A ratio calculated using the borrower’s total monthly debt payments on the total debt obligations, excluding mortgage and the requested LC loan, divided by the borrower’s self-reported monthly income.'),
    ('delinq_2yrs', 'The number of 30+ days past-due incidences of delinquency in the borrower\'s credit file for the past 2 years'),
    ('earliest_cr_line', 'The month the borrower\'s earliest reported credit line was opened'),
    ('inq_last_6mths', 'The number of inquiries in past 6 months (excluding auto and mortgage inquiries)'),
    ('mths_since_last_delinq', 'The number of months since the borrower\'s last delinquency.'),
    ('mths_since_last_record', 'The number of months since the last public record.'),
    ('open_acc', 'The number of open credit lines in the borrower\'s credit file.'),
    ('pub_rec', 'Number of derogatory public records'),
    ('revol_bal', 'Total credit revolving balance'),
    ('next_pymnt_d', 'Next scheduled payment date'),
    ('last_credit_pull_d', 'The most recent month LC pulled credit for this loan'),
    ('pub_rec_bankruptcies', 'Number of public record bankruptcies')
])


# target variable
TARGET = 'loan_status'


# remove for other reasons
REMOVE_VAR = [
    'emp_title',  # regulations/too many values
    'desc',  # hard to extract feature
    'zip_code',  # we already have addr_state
    'title',  # we already have purpose'
    'grade',
    'sub_grade',
    'title',
    'funded_amnt',
    'funded_amnt_inv',
    'debt_settlement_flag',  # settlement not included in target
    'debt_settlement_flag_date',
    'settlement_status',
    'settlement_date',
    'settlement_amount',
    'settlement_percentage',
    'settlement_term'
]


# all NAN
EMPTY_VAR = [
    'id',
    'member_id',
    'url',
    'mths_since_last_major_derog',
    'annual_inc_joint',
    'dti_joint',
    'verification_status_joint',
    'tot_coll_amt',
    'tot_cur_bal',
    'open_acc_6m',
    'open_act_il',
    'open_il_12m',
    'open_il_24m',
    'mths_since_rcnt_il',
    'total_bal_il',
    'il_util',
    'open_rv_12m',
    'open_rv_24m',
    'max_bal_bc',
    'all_util',
    'total_rev_hi_lim',
    'inq_fi',
    'total_cu_tl',
    'inq_last_12m',
    'acc_open_past_24mths',
    'avg_cur_bal',
    'bc_open_to_buy',
    'bc_util',
    'mo_sin_old_il_acct',
    'mo_sin_old_rev_tl_op',
    'mo_sin_rcnt_rev_tl_op',
    'mo_sin_rcnt_tl',
    'mort_acc',
    'mths_since_recent_bc',
    'mths_since_recent_bc_dlq',
    'mths_since_recent_inq',
    'mths_since_recent_revol_delinq',
    'num_accts_ever_120_pd',
    'num_actv_bc_tl',
    'num_actv_rev_tl',
    'num_bc_sats',
    'num_bc_tl',
    'num_il_tl',
    'num_op_rev_tl',
    'num_rev_accts',
    'num_rev_tl_bal_gt_0',
    'num_sats',
    'num_tl_120dpd_2m',
    'num_tl_30dpd',
    'num_tl_90g_dpd_24m',
    'num_tl_op_past_12m',
    'pct_tl_nvr_dlq',
    'percent_bc_gt_75',
    'tot_hi_cred_lim',
    'total_bal_ex_mort',
    'total_bc_limit',
    'total_il_high_credit_limit',
    'revol_bal_joint',
    'sec_app_earliest_cr_line',
    'sec_app_inq_last_6mths',
    'sec_app_mort_acc',
    'sec_app_open_acc',
    'sec_app_revol_util',
    'sec_app_open_act_il',
    'sec_app_num_rev_accts',
    'sec_app_chargeoff_within_12_mths',
    'sec_app_collections_12_mths_ex_med',
    'sec_app_mths_since_last_major_derog',
    'hardship_type',
    'hardship_reason',
    'hardship_status',
    'deferral_term',
    'hardship_amount',
    'hardship_start_date',
    'hardship_end_date',
    'payment_plan_start_date',
    'hardship_length',
    'hardship_dpd',
    'hardship_loan_status',
    'orig_projected_additional_accrued_interest',
    'hardship_payoff_balance_amount',
    'hardship_last_payment_amount'
]


# low variance or zero variance variables
LOW_VAR = [
    'pymnt_plan',
    'initial_list_status',
    'out_prncp',
    'out_prncp_inv',
    'collections_12_mths_ex_med',
    'policy_code',
    'application_type',
    'acc_now_delinq',
    'chargeoff_within_12_mths',
    'delinq_amnt',
    'tax_liens',
    'hardship_flag',
    'disbursement_method'
]


# specify rounding of variables for display
ROUNDER = {
    'int_rate': 4,
    'installment': 2,
    'annual_inc': 2,
    'dti': 2,
    'revol_bal': 2,
    'credit_age': 4}

def fe(df, is_tree=True):
    """
    Function to feature engineering.
    
    Parameters
    ----------
    df: a pandas dataframe
    
    is_tree: 
        If True, prepare data for a tree model 
    
    Returns
    ----------
    df, target, cat_idx, rounder : tuple
        Data, target, id of categorical variables, list of rounding digits of continuous variables
    """

    # take the variables of interest and remove null rows
    df = df.loc[:, GOOD_VAR.keys()]
    keep_idx = np.logical_not(df.isnull().apply(all, axis=1))
    df = df[keep_idx]

    # filter out some NANs and targets that aren't 'Charged Off' or 'Fully Paid'
    idx = np.logical_not(df['delinq_2yrs'].isnull() | df['last_credit_pull_d'].isnull() | df['pub_rec_bankruptcies'].isnull())
    idx = np.logical_and(idx, df['loan_status'].isin(['Charged Off', 'Fully Paid']))
    df = df.loc[idx]

   # useless
    df.drop(['next_pymnt_d', 'last_credit_pull_d'], axis=1, inplace=True)

    # make credit age
    df.loc[:, 'issue_d'] = pd.to_datetime(df.loc[:, 'issue_d'], format='%b-%y')
    df.loc[:, 'earliest_cr_line'] = pd.to_datetime(df.loc[:, 'earliest_cr_line'], format='%b-%y')
    df.loc[:, 'credit_age'] = (df['issue_d'] - df['earliest_cr_line']).apply(lambda x: x.days/365)

    # order by date then extract
    df.sort_values('issue_d', inplace=True)
    issue_d = df.loc[:, 'issue_d']
    df.drop(['earliest_cr_line', 'addr_state', 'issue_d'], axis=1, inplace=True)

    # interest rate to percent
    df.loc[:, 'int_rate'] = df['int_rate'].apply(lambda x: float(x.rstrip('%'))/100)

    # replace NANs
    idx1 = df.loc[:, 'emp_length'].isnull()
    idx2 = df.loc[:, 'emp_length'] == 'n/a'
    df.loc[np.logical_or(idx1, idx2), 'emp_length'] = '0'

    if is_tree:
        df.fillna(999, inplace=True)
    else:
        missing = ['mths_since_last_delinq', 'mths_since_last_record']
        for var in missing:
            new_var = var + '_isNA'
            idx = df.loc[:, var].isnull()
            df.loc[:, new_var] = idx
            df.loc[idx, var] = np.mean(df.loc[np.logical_not(idx), var])

    # purpose columns to file under other
    move_to_other = ['moving', 'house', 'vacation', 'educational', 'renewable_energy']
    idx = df.purpose.isin(move_to_other)
    df.loc[idx, 'purpose'] = 'other'

    # ordinal var: emp_length
    df = df.assign(emp_length_yrs=df.emp_length.str.extract('(\d+)', expand=False).astype(np.float32))
    idx = df.emp_length_yrs.isnull().values
    df.drop('emp_length', axis=1, inplace=True)

    # categorical features
    cat_cols = 'term home_ownership verification_status purpose'.split(' ')
    df = pd.get_dummies(df, prefix=cat_cols, columns=cat_cols)

    # split target and input data
    d = {'Fully Paid': 1, 'Charged Off': 0}
    target = np.array(df.loc[:, 'loan_status'].apply(lambda x: d[x]))
    df.drop('loan_status', axis=1, inplace=True)
    print('Target encoding: {:s}={:d}, {:s}={:d}'.format(*reduce(lambda e1, e2: e1+e2, d.items())))

    df.rename(
        index=str,
        columns=dict(zip(df.columns, [name.replace(' ', '') for name in df.columns])),
        inplace=True)

    rounder = get_rounder(df.columns)

    if not is_tree:
        cat_cols = ['mths_since_last_delinq_isNA', 'mths_since_last_record_isNA'] + cat_cols
    cat_idx = find_categoricals(df.columns, cat_cols)

    print('lendingclub data: {:d} rows x {:d} cols'.format(*df.shape))

    return df, target, cat_idx, rounder


def find_categoricals(names, prefs):
    return [[i for i, name in enumerate(names) if name.startswith(pref)] for pref in prefs]


def get_rounder(names):
    rounder = ROUNDER.copy()
    new_cols = list(set(names).difference(set(ROUNDER)))
    rounder.update(dict(zip(new_cols, [0]*len(new_cols))))
    return rounder
