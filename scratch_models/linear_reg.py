import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy.stats import f, t
import matplotlib.pyplot as plt

data = (
    pd.read_csv(
        "https://raw.githubusercontent.com/m-clark/generalized-additive-models/master/data/pisasci2006.csv"
    )
    .drop(columns="Country")
    .dropna()
    .reset_index(drop=True)
)


class BaseMetrics:
    def __init__(self, X, y, intercept):
        if intercept:
            self.X = np.insert(X, 0, 1, axis=1)
        else:
            self.X = X.to_numpy()

        self._cols = X.columns
        self.intercept = intercept
        self._n = self.X.shape
        self.y = y.to_numpy()
        self.comp = np.linalg.inv(self.X.T @ self.X)

    def coefficients(self):
        return self.comp @ self.X.T @ self.y

    def fitted(self):
        return self.X @ self.coefficients()

    def residuals(self):
        return self.y - self.fitted()

    def _ss_error(self):
        return (self.residuals() ** 2).sum()

    def _ss_total(self):
        return (self.y**2).sum() - (
            self.y.sum() ** 2 / self._n[0] if self.intercept else 0
        )

    def _ss_model(self):
        return self._ss_total() - self._ss_error()

    def df_error(self):
        return self._n[0] - self._n[1]

    def sigma(self):
        return np.sqrt(self._ss_error() / self.df_error())

    def _mse_total(self):
        return self._ss_total() / (self._n[0] - 1)

    def df_model(self):
        return self._n[1] - 1 if self.intercept else self._n[1]

    def _mse_model(self):
        return self._ss_model() / self.df_model()

    def f_value(self):
        return self._mse_model() / (self.sigma() ** 2)

    def _loglik(self):

        return (
            -self._n[0] * np.log(2 * np.pi) / 2
            - self._n[0] * np.log(self.sigma())
            - self._ss_error() / (2 * self.sigma() ** 2)
        )

    def _aic(self):
        return - 2 * self._loglik() + 2 * self._n[1]

    def _bic(self):
        return - 2 * self._loglik() + self._n[1] * np.log(self._n[0])

    def f_pvalue(self):
        return 1 - f.cdf(self.f_value(), self.df_model(), self.df_error())

    def rsquared(self):
        return self._ss_model() / self._ss_total()

    def adj_rsquared(self):
        return 1 - (self.sigma() ** 2) / self._mse_total()

    def _coefficients_var(self):
        return self.sigma() * np.sqrt(np.diag(self.comp))

    def t_value(self):
        return self.coefficients() / self._coefficients_var()

    def t_pvalue(self):
        return (1 - t.cdf(abs(self.t_value()), self.df_error())) * 2

    def rstandard(self):
        return self.residuals() / self.sigma()

    def _hat(self):
        return self.X @ self.comp @ self.X.T

    def rstudent(self):
        return self.residuals() / (self.sigma() * np.sqrt(1 - np.diag(self._hat())))

    def _cook_distance(self):
        return (self.rstudent() ** 2 * np.diag(self._hat())) / (
            self._n[1] * (1 - np.diag(self._hat()))
        )


class LinearRegression(BaseMetrics):
    def __init__(self, X, y, intercept=True):
        super().__init__(X, y, intercept)

    def fit(self):
        return self

    def predict(self, X):
        if self.intercept:
            preds = (
                X.reindex(["C", *self._cols], axis=1).assign(C=1).to_numpy()
                @ self.coefficients()
            )
            return preds
        else:
            preds = X.reindex([*self._cols], axis=1).to_numpy() @ self.coefficients
            return preds

    def diagnostics(self, X=None):
        if X:
            pass
        else:
            fig, ax = plt.subplots(2, 2, figsize=(12, 6))
            ind = [*range(1, self._n[0] + 1)]
            sns.scatterplot(
                x=self.X @ self.coefficients(), y=self.residuals(), ax=ax[0, 0]
            )
            ax[0, 0].axhline(0, color="red")
            sm.qqplot(self.residuals(), line="q", ax=ax[1, 0])
            sns.scatterplot(x=ind, y=self._cook_distance(), ax=ax[0, 1])
            sns.scatterplot(x=ind, y=np.diag(self._hat()), ax=ax[1, 1])


X = data.drop(columns="Overall")
y = data.Overall

reg = LinearRegression(X=X, y=y, intercept=True).fit()
