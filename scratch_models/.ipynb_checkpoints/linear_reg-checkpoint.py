import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
import scipy.stats as st
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
            self._cols = X.columns.insert(0, "Intercept")
        else:
            self.X = X.to_numpy()
            self._cols = X.columns

        self.intercept = intercept
        self._n = self.X.shape
        self._ycol = y.name
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
        return -2 * self._loglik() + 2 * self._n[1]

    def _bic(self):
        return -2 * self._loglik() + self._n[1] * np.log(self._n[0])

    def f_pvalue(self):
        return 1 - st.f.cdf(self.f_value(), self.df_model(), self.df_error())

    def rsquared(self):
        return self._ss_model() / self._ss_total()

    def adj_rsquared(self):
        return 1 - (self.sigma() ** 2) / self._mse_total()

    def _coefficients_var(self):
        return self.sigma() * np.sqrt(np.diag(self.comp))

    def _coefficients_ic(self, significance=0.05):
        tpvalue = st.t.ppf(1 - significance / 2, self._n[0] - self._n[1])
        error = tpvalue * self._coefficients_var()
        return self.coefficients() - error, self.coefficients() + error

    def t_value(self):
        return self.coefficients() / self._coefficients_var()

    def t_pvalue(self):
        return (1 - st.t.cdf(abs(self.t_value()), self.df_error())) * 2

    def rstandard(self):
        return self.residuals() / self.sigma()

    def _hat(self):
        return self.X @ self.comp @ self.X.T

    def rstudent(self):
        return self.residuals() / (self.sigma() * np.sqrt(1 - np.diag(self._hat())))

    def _get_residuals(self, which="regression"):
        match which:
            case "regression":
                return self.residuals()
            case "studentized":
                return self.rstudent()
            case "standardized":
                return self.rstandard()

    def _cook_distance(self):
        return (self.rstudent() ** 2 * np.diag(self._hat())) / (
            self._n[1] * (1 - np.diag(self._hat()))
        )

    def _some_sup_tests(
        self, res="regression", test_norm="shapiro", test_het="breusch"
    ):
        residuals = self._get_residuals(res)

        match test_norm:
            case "lilliefors":
                normality = sm.stats.diagnostic.lilliefors(residuals)
            case "shapiro":
                normality = st.shapiro(residuals)
            case "anderson":
                normality = st.anderson(residuals)
            case _:
                raise ValueError(f"{test_norm} isn't supported in scratch_models")

        match test_het:
            case "breusch":
                het = sm.stats.diagnostic.het_breuschpagan(self.residuals(), self.X)
            case "gold":
                het = sm.stats.diagnostic.het_goldfeldquandt(self.y, self.X)
            case _:
                raise ValueError(f"{test_het} isn't supported in scratch_models")

        return {"Normality": normality[0:2], "heteroscedasticity": het[0:2]}

    def summary(self):

        some_stats_left = [
            ("Dep. Variable:", self._ycol),
            ("Log-Likelihood:", self._loglik()),
            ("F-statistic:", self.f_value()),
            ("Df Model:", self.df_model()),
            ("BIC:", self._bic()),
        ]

        some_stats_right = [
            ("R-squared:", self.rsquared()),
            ("Adj. R-squared:", self.adj_rsquared()),
            ("Prob (F-statistic):", self.f_pvalue()),
            ("Df Residuals:", self.df_error()),
            ("AIC:", self._aic()),
        ]

        some_star = "*" * 80

        print("LinearRegression".center(80))
        print(some_star)

        for i in range(len(some_stats_left)):
            right_vals1 = some_stats_right[i][0]
            right_vals2 = some_stats_right[i][1]
            left_vals1 = some_stats_left[i][0]
            left_vals2 = some_stats_left[i][1]
            diff_left = 39 - len(left_vals1)
            diff_right = 36 - len(right_vals1)
            string_right = f"  {right_vals1} {right_vals2:>{diff_right}.3f}"
            if isinstance(left_vals2, str):
                print(f"{left_vals1} {left_vals2:>{diff_left}}", string_right)
            else:
                print(f"{left_vals1} {left_vals2:>{diff_left}.3f}", string_right)

        print(some_star)
        print(
            " " * 20
            + f"{'coef':<9} {'std err':<10} {'t':<10} {'P>|t|':<10} {'[0.025':<10} {'0.975]':<10}"
        )

        print("-" * 80)
        for i in range(len(self._cols)):
            coef, std_err = self.coefficients()[i], self._coefficients_var()[i]
            t_val, p_val = self.t_value()[i], self.t_pvalue()[i]
            interval_low, interval_high = (
                self._coefficients_ic()[0][i],
                self._coefficients_ic()[1][i],
            )
            p_val_formatted = (
                "< 2e-16"
                if p_val < 2e-16
                else f"{p_val:.3f}" if p_val >= 1e-3 else f"{p_val:.2e}"
            )
            print(
                f"{self._cols[i][0:16]:<18} {coef:<10.4f} {std_err:<10.3f} {t_val:<10.3f} {p_val_formatted:<10} {interval_low:<10.3f} {interval_high:<10.3f}"
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

    def vis_normal(self, **kwargs):
        _, ax = plt.subplots(ncols=2, figsize=(12, 6))
        residuals = self._get_residuals(**kwargs)
        x = np.linspace(np.min(residuals), np.max(residuals), 1000)
        y = st.norm.pdf(x, np.mean(residuals), np.std(residuals))
        sm.qqplot(residuals, line="q", ax=ax[0])
        sns.kdeplot(x=residuals, ax=ax[1])
        sns.lineplot(x=x, y=y, ax=ax[1], color="red")

    def vis_linear(self, **kwargs):
        sns.relplot(x=self.y, y=self.fitted(), **kwargs) \
        .set_axis_labels("Obs. values", "Fitted values") \
        .ax.axline(xy1 = (0, 0), slope = 1, color="gray", alpha=0.4, dashes=(2, 2))

    def vis_homo(self, which="regression", **kwargs):
        residuals = self._get_residuals(which=which)
        sns.relplot(x=self.fitted(), y=residuals, **kwargs) \
        .set_axis_labels("Fitted values", "Residuals") \
        .ax.axline(xy1 = (0, 0), slope = 0, color="gray", alpha=0.4, dashes=(2, 2))

    def vis_arr(self, which="regression", **kwargs):
        residuals = self._get_residuals(which)
        sns.relplot(x=range(self._n[0]), y=residuals, **kwargs) \
        .set_axis_labels("Index", "Residuals") \
        .ax.axline(xy1 = (0, 0), slope = 0, color="gray", alpha=0.4, dashes=(2, 2))

    def vis_anomalies(self, significance=0.5, **kwargs):
        fig, ax = plt.subplots(ncols=2, figsize=(12, 6))
        h = np.diag(self._hat())
        residuals = self._get_residuals(which="studentized")
        sns.scatterplot(x=self.fitted(), y=h, ax=ax[0], **kwargs)
        ax[0].axline(xy1 = (0, 2 * self._n[1] / self._n[0]),
                   slope = 0, color="gray", alpha=0.4, dashes=(2, 2))
        ax[0].set_xlabel("Fitted values")
        ax[0].set_ylabel("hii")
        

        li_cook = st.f.ppf(0.5, significance, self._n[1], self._n[0] - self._n[1])
        sns.scatterplot(x=self.fitted(), y=self._cook_distance(), ax=ax[1], **kwargs)
        ax[1].axline(xy1 = (0, li_cook), slope=0, color="gray", dashes=(2, 2))
        ax[1].set_xlabel("Fitted values")
        ax[1].set_ylabel("Di")

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
