import numpy as np
import pandas as pd
import seaborn as sns

data = (
    pd.read_csv('https://raw.githubusercontent.com/m-clark/generalized-additive-models/master/data/pisasci2006.csv')
    .drop(columns='Country')
    .dropna()
    .reset_index(drop=True)
    )


class LinearRegression:
    def __init__(self, X, y, intercept=True):

        if intercept:
            self.X = X.reindex(['C', *X.columns], axis=1).assign(C=1).to_numpy()
        else:
            self.X = X.to_numpy()

        self.sigma = None
        self.residuals = None
        self.intercept = intercept
        self._cols = X.columns
        self._n = X.shape
        self.y = y.to_numpy()

    def estimate(self):
        comp = np.linalg.inv(self.X.T @ self.X)
        return comp @ self.X.T @ self.y

    def loglik(self):
        betas = self.estimate()
        mat_dif = self.y - self.X @ betas
        self.sigma = (mat_dif.T @ mat_dif) / (self._n[0] - betas.shape[0])
        
        exp_ = np.exp(- (mat_dif.T @ mat_dif) / (2 * self.sigma))

        return exp_ / ((2 * np.pi * self.sigma) ** (self._n[0] / 2))

    def predict(self, X):
        
        if self.intercept:
            preds = X.reindex(['C', *self._cols], axis=1).assign(C=1).to_numpy() @ self.estimate()
            self.residuals = self.y - preds
            return preds
        else:
            preds = X.reindex([*self._cols], axis=1).to_numpy() @ self.estimate()
            self.residuals = self.y - preds
            return preds

X = data.drop(columns='Overall')
y = data.Overall

reg = LinearRegression(X=X, y=y, intercept=False)
