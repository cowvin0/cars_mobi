import numpy as np
import pandas as pd
from functools import wraps
from scipy.optimize import minimize

data = (
    pd.read_csv('https://raw.githubusercontent.com/m-clark/generalized-additive-models/master/data/pisasci2006.csv')
    .drop(columns='Country')
    .dropna()
    .reset_index(drop=True)
    )


class LinearRegression:
    def __init__(self, X, y):
        self._cols = X.columns
        self._n = X.shape
        self.X = X.to_numpy()
        self.y = y.to_numpy()

    def estimate(self):
        comp = np.linalg.inv(self.X.T @ self.X)
        return comp @ self.X.T @ self.y


    def loglik(self):
        betas = self.estimate()
        mat_dif = self.y - self.X @ betas
        sigma = (mat_dif.T @ mat_dif) / (self._n[0] - betas.shape[0])
        exp_ = np.exp(- (mat_dif.T @ mat_dif) / (2 * sigma))

        return exp_ / ((2 * np.pi * sigma) ** (self._n / 2))

    def fit(self, X, y):
        return self.batata
        

X = data.drop(columns='Overall')
y = data.Overall

reg = LinearRegression(X=X, y=y)
