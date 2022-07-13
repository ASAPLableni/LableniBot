import json
import math
import time
import warnings
from collections import defaultdict
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import scipy as sp
import scipy.stats as stats

from scipy.spatial.distance import pdist, squareform
from sklearn import linear_model
from sklearn.metrics import r2_score


def get_p_string(p):
    if p >= 0.05:
        return "-"
    elif 0.01 <= p < 0.05:
        return "*"
    elif 0.001 <= p < 0.01:
        return "**"
    else:
        return "***"


def stat_print(list_x, name, precision=4, quantile=False):
    if quantile:
        print(
            "Mean " + name + " =", np.round(np.nanmean(list_x), precision),
            "+/-", np.round(np.nanstd(list_x), precision),
            "; Median =", np.round(np.nanmedian(list_x), precision),
            "; Min. = ", np.round(np.nanmin(list_x), precision),
            "; Max. = ", np.round(np.nanmax(list_x), precision),
            "\n Quantile 1%", np.round(np.nanquantile(list_x, 0.01), precision),
            "Quantile 99%", np.round(np.nanquantile(list_x, 0.99), precision)
        )
    else:
        print(
            "Mean " + name + " =", np.round(np.nanmean(list_x), precision),
            "+/-", np.round(np.nanstd(list_x), precision),
            "; Median =", np.round(np.nanmedian(list_x), precision),
            "; Min. = ", np.round(np.nanmin(list_x), precision),
            "; Max. = ", np.round(np.nanmax(list_x), precision)
        )


def make_scatter_plot(df, x_feat, x_name, y_feat, y_name, alpha_th=0.6, fontsize_th=14, lr_mode=True):
    data_idx = df[[x_feat, y_feat]].dropna().index.values

    corr_v, corr_pvalue = stats.pearsonr(df.loc[data_idx, x_feat].values, df.loc[data_idx, y_feat].values)
    print("Correlation value", corr_v)
    print("P-value", get_p_string(corr_pvalue))

    plt.figure(figsize=(12, 5))

    if lr_mode:
        lr = linear_model.LinearRegression(n_jobs=-1)
        lr.fit(df.loc[data_idx, x_feat].values.reshape(-1, 1), df.loc[data_idx, y_feat])
        y_pred = lr.predict(df.loc[data_idx, x_feat].values.reshape(-1, 1))

        print("Coefficients: \n", lr.coef_, "\nIntercept: \n", lr.intercept_)
        print("R-square: %.2f" % r2_score(df.loc[data_idx, y_feat], y_pred))

        plt.plot(df.loc[data_idx, x_feat], y_pred, c="red", label="Linear Regression")
        plt.legend(fontsize=12)
        delta_int = np.abs(np.nanmax(df[y_feat]) - np.nanmin(df[y_feat]))
        plt.ylim(np.nanmin(df[y_feat]) - 0.1 * delta_int, np.nanmax(df[y_feat]) + 0.1 * delta_int)

    plt.scatter(df[x_feat], df[y_feat], alpha=0.6)

    plt.xlabel(x_name, fontsize=14)
    plt.ylabel(y_name, fontsize=14)

    plt.show()


def get_mahalanobis_dist(x_arr, centers=None):
    if centers is None:
        centers = np.mean(x_arr, axis=0)
    cov = np.cov(x_arr.astype(float).T)
    inv_covariance_matrix = sp.linalg.inv(cov)
    left_term = np.dot(x_arr - centers, inv_covariance_matrix)
    mahal = np.dot(left_term, (x_arr - centers).T)

    return mahal.diagonal()
