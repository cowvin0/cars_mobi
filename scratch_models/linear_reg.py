import numpy as np
import pandas as pd
import seaborn as sns
from scipy.stats import f, t

data = (
    pd.read_csv(
        "https://raw.githubusercontent.com/m-clark/generalized-additive-models/master/data/pisasci2006.csv"
    )
    .drop(columns="Country")
    .dropna()
    .reset_index(drop=True)
)


class LinearRegression:
    def __init__(self, X, y, intercept=True):
        if intercept:
            self.X = X.reindex(["C", *X.columns], axis=1).assign(C=1).to_numpy()
        else:
            self.X = X.to_numpy()

        self.intercept = intercept
        self._cols = X.columns
        self._n = self.X.shape
        self.y = y.to_numpy()

    def fit(self):
        comp = np.linalg.inv(self.X.T @ self.X)
        self.diag = comp
        self.coefs = comp @ self.X.T @ self.y
        self.residuals = self.y - np.dot(self.X, self.coefs)
        self.sse = (self.residuals**2).sum()
        self.df_res = self._n[0] - self.coefs.shape[0]
        self.df_model = self._n[1]
        self.sigma = np.sqrt(self.sse / self.df_res)
        self.sst = (self.y**2).sum() - (
            self.y.sum() ** 2 / self._n[0] if self.intercept else 0
        )
        self.mst = self.sst / (self._n[0] - 1)
        self.ssr = self.sst - self.sse
        self.msr = self.ssr / (self.df_model - 1 if self.intercept else self._n[1])
        self.fstatistic = self.msr / (self.sigma**2)
        self.f_pvalue = 1 - f.cdf(self.fstatistic, self.df_model, self.df_res)
        self.rsquared = self.ssr / self.sst
        self.rsquared_adj = 1 - (self.sigma**2) / self.mst
        self.coefs_var = self.sigma * np.sqrt(np.diag(comp))
        self.tstatistic = self.coefs / self.coefs_var
        self.t_pvalue = (1 - t.cdf(abs(self.tstatistic), self.df_res)) * 2
        self._hat = self.X @ comp @ self.X.T
        self.std_residuals = self.residuals / (
            np.sqrt(self.sigma**2 * (1 - np.diag(self._hat)))
        )
        self.cook_distance = (self.std_residuals**2 * np.diag(self._hat)) / (
            self._n[1] * (1 - np.diag(self._hat))
        )
        return self

    def predict(self, X):
        if self.intercept:
            preds = (
                X.reindex(["C", *self._cols], axis=1).assign(C=1).to_numpy()
                @ self.coefs
            )
            self.residuals = self.y - preds
            return preds
        else:
            preds = X.reindex([*self._cols], axis=1).to_numpy() @ self.coefs
            self.residuals = self.y - preds
            return preds


X = data.drop(columns="Overall")
y = data.Overall

reg = LinearRegression(X=X, y=y, intercept=True).fit()
