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
import glob
import scipy.stats


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
        self.models_ = [0] * X.shape[1]
        self.ages_ = y
        voxels = np.transpose(X)
        ages_t = y.reshape(-1, 1)
        self.ages_grid_ = np.arange(15, 100, 5).reshape(-1, 1)
        kernel = (
            44.7 ** 2
            * skg.kernels.RBF(length_scale=30, length_scale_bounds=(10, 60))
            + skg.kernels.WhiteKernel(noise_level=1e4,
                                      noise_level_bounds=(1e3, 1e5))
        )
        ages_kde = skn.KernelDensity(kernel="gaussian", bandwidth=3)
        ages_kde.fit(ages_t)
        prior = np.exp(
            ages_kde.score_samples(self.ages_grid_))
        self.prior_ = prior / np.sum(prior)
        self.models_ = []
        for i, voxel in tqdm.tqdm(enumerate(voxels)):
            slope, intercept, _, _, _ = scipy.stats.linregress(y, voxel)
            residuals = np.abs(voxel - slope * y - intercept)
            gp = skg.GaussianProcessRegressor(
                kernel=kernel,
                n_restarts_optimizer=0)
            gp.fit(ages_t, residuals)
            item = slope * self.ages_grid_.flatten() + intercept, gp.predict(self.ages_grid_)
            self.models_.append(item)
        return self

    def predict(self, X):
        try:
            getattr(self, "models_")
            getattr(self, "ages_")
        except AttributeError:
            raise RuntimeError("You must train the regressor before predicting data!")
        zs = np.zeros(shape=(X.shape[0], X.shape[1], self.ages_grid_.shape[0]))
        for i, (model, voxels) in tqdm.tqdm(enumerate(
                zip(self.models_, np.transpose(X)))):
            for j, age in enumerate(self.ages_grid_):
                mean, noise = model[0][j], model[1][j]
                prob_voxel_given_age = scipy.stats.norm.pdf(
                    (voxels - mean) / noise)
                prob_age_given_voxel = prob_voxel_given_age
                zs[:, i, j] = prob_age_given_voxel
        zs /= np.sum(zs, axis=2, keepdims=True)
        mean_ages = np.mean(
            np.inner(zs, self.ages_grid_.flatten()),
            axis=1)
        return mean_ages.astype(int)


@click.command()
@click.argument("input_ages", nargs=1)
@click.argument("train_folder", nargs=1)
def main(input_ages, train_folder):
    train_files = glob.glob(os.path.join(train_folder, "*"))
    train = [0] * len(train_files)
    ages = np.array(
        [int(age)
         for age in open(input_ages).read().split()])
    indices = np.random.randint(
        0,
        40000,
        1000)
    for file_name in train_files:
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        train[i] = np.load(file_name)[indices]
        # train[i] = np.load(file_name)
    train = np.array(train)
    kf = sklearn.model_selection.KFold(n_splits=3)
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
        print(mse)
        errors.append(mse)
    print("MSE: ", sum(errors) / len(errors))


if __name__ == "__main__":
    main()
