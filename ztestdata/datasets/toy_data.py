##
## Copyright 2024 Zest AI All Rights Reserved
##
##
##
## It is prohibited to copy, in whole or in part, modify, directly or indirectly reverse engineer, disassemble, decompile, decode or adapt this code or any portion or aspect thereof, or otherwise attempt to derive or gain access to any part of the source code or algorithms contained herein as provided in your ZAML agreement.
##
import os
import numpy as np
import scipy as sp
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import QuantileTransformer

from .scalers import ZamlScaler


def boston_data(scaler_type='identity'):
    """
    Load and preprocess boston house dataset.
    
    Parameters
    ----------
    scaler_type : str, default='identity'
        Name of scaler type. Possible options: 'identity', 'robust', 'standardize', 'normalize'.
    
    Returns
    -------
    x, y, scaler : tuple
        Respectively: dataset with variables, target, scaler.
    """
    
    csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'boston_house.csv'))
    df = pd.read_csv(csv)
    x = df.drop('target', axis=1)
    y = df['target']
    scaler = ZamlScaler(scaler_type=scaler_type)
    return x, y, scaler


def almost_boston(model_type='classification', force_disparity=True):
    """
    Load and preprocess boston house dataset with protected classes.
    
    Parameters
    ----------
    model_type : str, default='classification'
        If 'classification', the data is prepared for the classification model. Otherwise for the regression model.
    
    force_disparity : boolean, default=True
        If True in the target there are disparities.
    
    Returns
    -------
    x, y, z_mask: tuple
        Respectively: dataset with variables, target, protected classes mask.
    """
    
    
    csv = os.path.abspath(os.path.join(os.path.dirname(__file__), 'boston_house.csv'))
    df = pd.read_csv(csv)
    
    # create input data
    x = df.drop('target', axis=1)

    # define protected class (perfectly balanced)
    # 0 = less than median number of blacks in area; 1 = more than median number
    z = (x['B'] > np.median(x['B'])).astype('int')
    z_mask = z.astype('bool')
    z_mask = z_mask.values
    x.drop(columns='B', inplace=True)
    
    # define target
    y = np.copy(df['target'])

    # inject disparity along class lines (reduce home prices of z class)
    if force_disparity:
        y[z_mask] = y[z_mask] * 0.35

    # define classification y
    # 0 = home value less than median; 1 = home value greater than median
    if model_type == 'classification':
        y = (y > np.median(y)).astype('int')

    return x, y, z_mask

# https://archive.ics.uci.edu/ml/datasets/adult
def census_income(path, synthetic_regression_target=False):
    """
    Load and preprocess census income data.
    
    Parameters
    ----------
    path : str
        Path to csv files with census income data.
    
    synthetic_regression_target : boolean, default=False
        If 'True' then the target is for the classification model.
    
    Returns
    -------
    X, y, Z: tuple
        Respectively: dataset with variables, target, protected classes mask.
    """

    column_names = ['age', 'workclass', 'fnlwgt', 'education', 'education_num',
                    'marital_status', 'occupation', 'relationship', 'race', 'gender',
                    'capital_gain', 'capital_loss', 'hours_per_week', 'country', 'target']
    input_data = (pd.read_csv(path, names=column_names,
                              na_values="?", sep=r'\s*,\s*', engine='python'))

    # sensitive attributes; we identify 'race' and 'sex' as sensitive attributes
    # 1 == non-white, 1 == non-male
    sensitive_attribs = ['race', 'gender']
    Z = (input_data.loc[:, sensitive_attribs]
         .assign(race=lambda df: (df['race'] != 'White').astype(int),
                 gender=lambda df: (df['gender'] != 'Male').astype(int)))

    # targets; 1 when someone makes over 50k , otherwise 0
    y = (input_data['target'] == '>50K').astype(int)

    # features; note that the 'target' and sentive attribute columns are dropped
    X = (input_data
         .drop(columns=['target', 'race', 'gender'])
         .fillna('Unknown')
         .pipe(pd.get_dummies, drop_first=True))

    # standardize the data
    scaler = StandardScaler().fit(X)
    scale_df = lambda df, scaler: pd.DataFrame(scaler.transform(df), columns=df.columns, index=df.index)
    X = X.pipe(scale_df, scaler)

    if synthetic_regression_target:
        #fit a simple logistic regression
        lr = LogisticRegression(random_state=0)
        lr.fit(X, y)
        qt = QuantileTransformer(output_distribution='normal')
        ts = sp.special.logit(lr.predict_proba(X)[:,1]) # back to margin space
        ts = ts - np.mean(ts) # zero mean
        ts = qt.fit_transform(ts.reshape(-1,1)) # transform into smooth uniform
        ts = ts.reshape(-1)
        Z_sum = np.sum(Z,axis=1)
        Z_sum_unique = np.unique(Z_sum)
        np.random.seed(111)
        for zval in Z_sum_unique:
            indx = Z_sum == zval
            indx = indx.values
            n_random = np.sum(indx)
            delta_ts = np.random.normal(loc=0.0, scale=1.0*(1.0+zval), size=n_random)
            ts[indx] = ts[indx]*10.0+56.0-1.0*zval+delta_ts # shift and scale
        ts[ts < 0.01] = 0.01 # clip negative values
        y = ts
    return X, y, Z

def census_income_data(synthetic_regression_target=False):
    """
    Load and preprocess census income data.
    
    Parameters
    ----------
    synthetic_regression_target : boolean, default=False
        If 'True' then the target is for the classification model.
        
    Returns
    -------
    X, y, Z : tuple
        Respectively: dataset with variables, target, protected classes mask.
    """
    census_income_path = os.path.join(
        os.path.abspath(os.path.dirname(__file__)),
        '.raw_data/census_income.data')
    return census_income(census_income_path,synthetic_regression_target)
