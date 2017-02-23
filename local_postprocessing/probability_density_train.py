from __future__ import division, print_function
import os
import click
import numpy as np
import tqdm
import sklearn.neighbors as skn
import sklearn.gaussian_process as skg
import sklearn.base
import sklearn.metrics
import sklearn.model_selection
import sklearn.preprocessing
import sklearn.pipeline
import sklearn.linear_model
import glob
import scipy.stats
import matplotlib.pyplot as plt
import csv


class AgeRegressor(sklearn.base.BaseEstimator,
                   sklearn.base.RegressorMixin):
    
    def __init__(
            self,
            kernel="gaussian",
            bandwidth=15,
            scaling_factor=15):
        self.kernel = kernel
        self.bandwidth = bandwidth
        self.scaling_factor = scaling_factor

    def fit(self, X, y):
        self.ages_ = y
        degree = 4
        ages_t = y.reshape(-1, 1)
        wm_model = sklearn.pipeline.make_pipeline(
            sklearn.preprocessing.PolynomialFeatures(degree),
            sklearn.linear_model.LinearRegression())
        gm_model = sklearn.pipeline.make_pipeline(
            sklearn.preprocessing.PolynomialFeatures(1),
            sklearn.linear_model.LinearRegression())
        self.wm_model_ = wm_model.fit(ages_t, X[:, 0])
        self.gm_model_ = gm_model.fit(ages_t, X[:, 1])

        self.ages_ = y
        self.ages_grid_ = np.arange(15, 100).reshape(-1, 1)
        ages_kde = skn.KernelDensity(kernel="gaussian", bandwidth=3)
        ages_kde.fit(ages_t)
        prior = np.exp(
            ages_kde.score_samples(self.ages_grid_))
        self.prior_ = prior / np.sum(prior)

        wm_residuals = np.abs(wm_model.predict(ages_t) - X[:, 0])
        gm_kernel = (
            44.7 ** 2
            * skg.kernels.RBF(length_scale=30, length_scale_bounds=(10, 60))
            + skg.kernels.WhiteKernel(noise_level=1e4,
                                      noise_level_bounds=(1e3, 1e5))
        )
        wm_kernel = (
            44.7 ** 2
            * skg.kernels.RBF(length_scale=30, length_scale_bounds=(10, 60))
            + skg.kernels.WhiteKernel(noise_level=1e4,
                                      noise_level_bounds=(1e3, 1e5))
        )
        self.wm_gp_ = skg.GaussianProcessRegressor(
            kernel=wm_kernel,
            n_restarts_optimizer=0)
        self.wm_gp_.fit(ages_t, wm_residuals)
        gm_residuals = np.abs(gm_model.predict(ages_t) - X[:, 1])
        self.gm_gp_ = skg.GaussianProcessRegressor(
            kernel=gm_kernel,
            n_restarts_optimizer=0)
        self.gm_gp_.fit(ages_t, gm_residuals)

        # plt.figure()
        # plt.scatter(y, X[:, 0])
        # plt.plot(self.ages_grid_, wm_model.predict(self.ages_grid_))
        # plt.figure()
        # plt.scatter(y, gm_residuals)
        # plt.plot(self.ages_grid_, self.gm_gp_.predict(self.ages_grid_))
        # plt.show()
        # input()
        return self

    def predict(self, X):
        try:
            getattr(self, "gm_model_")
        except AttributeError:
            raise RuntimeError("You must train the regressor before predicting data!")

        zs = np.zeros(shape=(X.shape[0], X.shape[1], self.ages_grid_.shape[0]))
        for i, age in enumerate(self.ages_grid_):
            wm_mean = self.wm_model_.predict(age.reshape(-1, 1))
            wm_noise = self.wm_gp_.predict(age.reshape(-1, 1))
            prob_wm_given_age = scipy.stats.norm.pdf((X[:, 0] - wm_mean) / wm_noise)
            prob_age_given_wm = prob_wm_given_age * self.prior_[i]
            gm_mean = self.gm_model_.predict(age.reshape(-1, 1))
            gm_noise = self.gm_gp_.predict(age.reshape(-1, 1))
            prob_gm_given_age = scipy.stats.norm.pdf((X[:, 1] - gm_mean) / gm_noise)
            prob_age_given_gm = prob_gm_given_age * self.prior_[i]
            zs[:, 0, i] = prob_age_given_wm
            zs[:, 1, i] = prob_age_given_gm
        zs /= np.sum(zs, axis=2, keepdims=True)
        mean_ages = np.inner(zs, self.ages_grid_.flatten())
        var_ages = np.inner(zs, self.ages_grid_.flatten() ** 2) - mean_ages ** 2
        return np.average(mean_ages, axis=1, weights=1 / var_ages).astype(int)
        # return mean_ages[:, 1].astype(int)


@click.command()
@click.argument("input_ages", nargs=1)
@click.argument("train_folder", nargs=1)
@click.argument("train_gm", nargs=1)
@click.argument("test_wm", nargs=1)
@click.argument("test_gm", nargs=1)
def main(input_ages, train_folder, train_gm, test_wm, test_gm):
    train_files = glob.glob(os.path.join(train_folder, "*"))
    train = [0] * len(train_files)
    ages = np.array(
        [int(age)
         for age in open(input_ages).read().split()])
    indices = np.random.randint(
        0,
        40000,
        1000)
    train_gm = glob.glob(os.path.join(train_gm, "*"))
    gm = np.zeros(len(train_gm))
    for file_name in train_gm:
        data = np.genfromtxt(file_name)
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        gm[i] = data

    wm = np.zeros_like(gm)
    for file_name in train_files:
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        # train[i] = np.load(file_name)[indices]
        a = np.load(file_name)
        train[i] = a
        wm[i] = np.size(a[a > 1000])

    train = np.vstack((wm, gm)).T
    kf = sklearn.model_selection.KFold(n_splits=5)
    errors = []
    for train_idx, test_idx in kf.split(train):
        x_train = train[train_idx]
        x_test = train[test_idx]
        y_train = ages[train_idx]
        y_test = ages[test_idx]
        estimator = AgeRegressor()
        estimator.fit(x_train, y_train)
        predictions = estimator.predict(x_test)
        mse = sklearn.metrics.mean_squared_error(y_test, predictions)
        errors.append(mse)
    print("MSE: ", sum(errors) / len(errors))


    test_gm = glob.glob(os.path.join(test_gm, "*"))
    gm = np.zeros(len(test_gm))
    for file_name in test_gm:
        data = np.genfromtxt(file_name)
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        gm[i] = data

    test_wm = glob.glob(os.path.join(test_wm, "*"))
    wm = np.zeros_like(gm)
    for file_name in test_wm:
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        # train[i] = np.load(file_name)[indices]
        a = np.load(file_name)
        wm[i] = np.size(a[a > 1000])

    test = np.vstack((wm, gm)).T
    estimator = AgeRegressor()
    estimator.fit(train, ages)
    prediction = estimator.predict(test)
    print(prediction)
    with open("white_matter.csv", "w") as outfile:
        writer = csv.writer(outfile)
        writer.writerow(["ID", "Prediction"])
        for i, pred in enumerate(prediction):
            writer.writerow([i + 1, pred])


if __name__ == "__main__":
    main()
