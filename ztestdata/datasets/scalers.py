##
## Copyright 2024 Zest AI All Rights Reserved
##
##
##
## It is prohibited to copy, in whole or in part, modify, directly or indirectly reverse engineer, disassemble, decompile, decode or adapt this code or any portion or aspect thereof, or otherwise attempt to derive or gain access to any part of the source code or algorithms contained herein as provided in your ZAML agreement.
##
from functools import reduce
import numpy as np
import pandas as pd
import sklearn.preprocessing as pre


def reshape(func):
    """
    Decorator to automatically handle array reshaping of first function arg

    This decorator takes a class method with some data as the first 
    positional argument, and prepares it for use:
      - asserts it is an np.ndarray or pd.DataFrame
      - if it is a dataframe extract the np array 
      - add singleton dimension for flat arrays
    """

    def new_func(self, x_in, *args, **kwargs):
        if len(x_in.shape) <= 1:
            if isinstance(x_in, pd.core.series.Series):
                assert False, 'You are trying to pass in a pd Series object. \
            Only numpy arrays and pandas DataFrame are accepted.)'
            if type(x_in) is np.ndarray:
                x_in = x_in.reshape((1, -1))
        if isinstance(x_in, pd.DataFrame):
            if hasattr(self, 'column_names'):
                if not self.column_names:
                    self.column_names = list(x_in.columns.values)
                else:
                    assert set(self.column_names) == set(list(x_in.columns.values)), \
                        'You are passing in a dataframe with different column names than ' \
                        'your underlying explainer. Please make sure you are using the correct column space.'
            if hasattr(self, 'column_names'):
                x = np.array(x_in[self.column_names])
            else:
                x = np.array(x_in)
        elif type(x_in) is np.ndarray:
            x = x_in
        else:
            raise TypeError('x must be a np.ndarray or pd.DataFrame')

        return func(self, x, *args, **kwargs)
    return new_func

def flatten_list(l):
    return np.array(reduce(lambda x, y: x + y, l))


def get_scaler(scaler_type):
    d = {
        'identity': IdentityScaler(),
        'robust': pre.RobustScaler(),
        'standardize': pre.StandardScaler(),
        'normalize': pre.Normalizer()}
    return d[scaler_type]


class IdentityScaler:
    def __init__(self):
        pass

    @reshape
    def fit_transform(self, x):
        return x

    @reshape
    def transform(self, x):
        return x

    @reshape
    def inverse_transform(self, x):
        return x


class ZamlScaler:
    """
    Class which helps transform and scale data.
    
    Parameters
    ----------
    cat_cols : list, default=[[]]
        Names of categorical features.
    
    scaler_type : str, default='identity'
        Name of scaler type. Possible options: 'identity', 'robust', 'standardize', 'normalize'.
    
    columns : list, default=[]
        Name of columns to transform
    
    rounder : list, default=None
        list of rounding digits of continuous variables
    """
    
    
    def __init__(self, cat_cols=[[]], scaler_type='identity', columns=[], rounder=None):
        self.cat_cols = cat_cols
        self.cat_idx = flatten_list(cat_cols)
        self.columns = np.array(columns)
        self.cat_scaler = get_scaler(scaler_type)
        self.cont_scaler = get_scaler(scaler_type)
        self.rounder = rounder

    @reshape
    def fit_transform(self, x):
        all_idx = np.arange(x.shape[1])
        self.cont_idx = np.setdiff1d(all_idx, self.cat_idx).astype(int)
        return self._scaler_operation(x, 'fit_transform')

    @reshape
    def transform(self, x):
        return self._scaler_operation(x, 'transform')

    @reshape
    def inverse_transform(self, x):
        return self._scaler_operation(x, 'inverse_transform')

    @reshape
    def as_dataframe(self, x, inverse_transform=True):
        """
        Transforming data to  pandas DataFrame.

        Parameters
        ----------
        x : numpy ndarray or pandas DataFrame shape (D,) or (N,D) 
            Data to transform to pandas DataFrame.
         
        inverse_transform : boolean, default=True
            If True, run the inverse transform of the scaler.

        Returns
        ----------
        df : pandas DataFrame
            A rounded, unscaled pandas DataFrame with named columns.
        """
        cols = self.columns if self.columns.size == x.shape[1] else None
        if inverse_transform:
            df = pd.DataFrame(self.inverse_transform(x), columns=cols)
        else:
            df = pd.DataFrame(self.transform(x), columns=cols)

        if self.rounder is not None:
            df = df.round(self.rounder)
        return df

    def _scaler_operation(self, x, mode):
        assert mode in ['fit_transform', 'transform', 'inverse_transform'], 'not a valid scaler operation'
        new_x = np.zeros(x.shape)
        if self.cat_idx.size > 0:
            new_x[:, self.cat_idx] = getattr(self.cat_scaler, mode)(x[:, self.cat_idx])
        if self.cont_idx.size > 0:
            new_x[:, self.cont_idx] = getattr(self.cont_scaler, mode)(x[:, self.cont_idx])

        return new_x
