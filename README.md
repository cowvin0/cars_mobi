The scratch_models is a regression library that implements a Multiple Linear Regression from scratch. It was inspired by the amazing *R programming language* and *Python statsmodels library*. The ideias here is to make it easy for you to check some assumptions around your linear regression model. Therefore, this package currently supports these features:

- You can fit a linear regression model
- It calculates metrics for your model, such as the Coefficient of Determination, ($R^2$ Adj) and RMSE.
- You also check assumptions of the linear model by plotting *residuals*, cook distance, check if there are influence observations.


```python
import scratch_models as sm
```

## Fit the model

It works similarly to LinearRegression class from scikit-learn, you just need to have a dataset and thus divide it by y and X. 


```python

```
