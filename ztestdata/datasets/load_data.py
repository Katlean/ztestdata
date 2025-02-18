##
## Copyright 2024 Zest AI All Rights Reserved
##
##
##
## It is prohibited to copy, in whole or in part, modify, directly or indirectly reverse engineer, disassemble, decompile, decode or adapt this code or any portion or aspect thereof, or otherwise attempt to derive or gain access to any part of the source code or algorithms contained herein as provided in your ZAML agreement.
##
"""

Important note to data makers:

  Models are explained in terms of the scaled data (which is what the model
  sees). With categorical values, some explainers need to derive
  sampling statistics, which are facilitated by OHE values. Explainers
  will treat everything like a continuous value by default unless you
  specify categorical columns. Please see 'lendingclub' as a key example
  of how to prepare a loan-style dataset.

"""
import os
import pandas as pd
import numpy as np
import sklearn.datasets as ds

from .feature_engineering import fe
from .scalers import ZamlScaler


def load_data(dataset, scaler_type='identity', **kwargs):
    """
    Load and preprocess various datasets.

    Supported:
      - lendingclub
      - max
      - simple
      - xor
      - ring
      - moons
      - correlated
      - mv_gate
      
    Parameters
    ----------
    dataset: str
        Name of selected dataset.
    
    scaler_type : str, default='identity'
        Name of scaler type. Possible options: 'identity', 'robust', 'standardize', 'normalize'.
    
    Returns
    -------
    x, y, scaler : tuple
        Respectively: dataset with variables, target, scaler.
    """
    # default params
    params = {
        'N': 10000,
        'noise_dim': 0,
        'is_tree': True}
    params.update(kwargs)
    N, noise_dim, is_tree = params['N'], params['noise_dim'], params['is_tree']

    scaler = ZamlScaler(scaler_type=scaler_type)

    if dataset == 'lendingclub':
        # TODO: This breaks if we don't ship the data/ directory into site-packages
        csv = os.path.abspath(os.path.join(os.path.dirname(__file__), './LoanStats3a.csv.bz2'))
        df = pd.read_csv(csv, low_memory=False, encoding='latin-1')

        df, y, cat_cols, rounder = fe(df, is_tree=is_tree)

        scaler = ZamlScaler(
            cat_cols=cat_cols,
            scaler_type=scaler_type,
            columns=df.columns,
            rounder=rounder)

        x = scaler.fit_transform(np.array(df).astype(np.float32))

    elif dataset == 'max':
        x = np.random.randn(N, 2 + noise_dim).astype(np.float32)
        y = np.max(x[:, :2], axis=1).astype(np.float32)

    elif dataset == 'simple':
        x = np.random.randn(N, 1 + noise_dim).astype(np.float32)
        y = x[:, 0] > 0

    elif dataset == 'xor':
        x = np.random.randn(N, 2 + noise_dim).astype(np.float32)
        y = np.logical_xor(x[:, 0] > 0, x[:, 1] > 0).astype(np.float32)

    elif dataset == 'correlated':
        x = np.random.randn(N, 1)
        x = np.concatenate(
            [x, x+0.1*np.random.randn(N, 2), np.random.randn(N, noise_dim)],
            axis=1).astype(np.float32)
        y = np.sum(x[:, :3], axis=1).astype(np.float32)

    elif dataset == 'ring':
        x, y = ds.make_circles(n_samples=N, noise=0.1)

    elif dataset == 'moons':
        x, y = ds.make_moons(n_samples=N, noise=0.1, random_state=1337)

    elif dataset == 'mv_gate':
        x = np.random.randn(N, noise_dim+4).astype(np.float32)
        y = (x[:, 0] + x[:, 1] * np.logical_xor(x[:, 2] > 0, x[:, 3] > 0)).astype(np.float32)

    else:
        assert False, 'dataset not supported'

    return x, y, scaler
