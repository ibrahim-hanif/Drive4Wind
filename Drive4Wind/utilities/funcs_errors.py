# Defining error functions for time series data comparison or fitting (regression)
# references:
# - 1. https://towardsdatascience.com/time-series-forecast-error-metrics-you-should-know-cc88b8c67f27/
# - 2. https://medium.com/@injure21/time-series-forecasting-metrics-a-practical-guide-72bba61fc2da

import numpy as np

def mapError( yPred, yTrue ):
    "Mean Absolute Percentage Error"
    N = len(yTrue)
    return np.sum( np.abs( (yPred-yTrue) / yTrue )*1e2 )/N

def rmsError( yPred, yTrue ):
    "Root Mean Square Error"
    N = len(yTrue)
    return np.sqrt( np.sum((yPred-yTrue)**2)/N )