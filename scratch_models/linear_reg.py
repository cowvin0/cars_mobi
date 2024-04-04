import numpy as np
import pandas as pd

class LinearRegression:
    def __init__(self, intercept=1):
        self.intercept = intercept

    def fit(self, X, y):

        estimate_beta = np.linalg.inv(np.dot(X.T, X))