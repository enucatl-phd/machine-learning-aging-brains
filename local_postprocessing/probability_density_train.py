import os
import click
import numpy as np
import tqdm
import sklearn.neighbors as skn
import sklearn.base
import glob


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
        self.kdes_ = [0] * X.shape[1]
        voxels = np.transpose(X)
        for i, voxel in tqdm.tqdm(enumerate(voxels)):
            ar = np.vstack((y, voxel / self.scaling_factor)).T
            kde = skn.KernelDensity(
                kernel=self.kernel,
                bandwidth=self.bandwidth)
            kde.fit(ar)
            self.kdes_[i] = kde
        return self

    def predict(self, X):
        try:
            getattr(self, "kdes_")
        except AttributeError:
            raise RuntimeError("You must train the regressor before predicting data!")
        ages = np.arange(15, 95, 5)
        zs = np.zeros(shape=(X.shape[0], X.shape[1], ages.shape[0]))
        for i, (kde, voxels) in tqdm.tqdm(enumerate(
                zip(self.kdes_, np.transpose(X)))):
            xx, yy = np.meshgrid(ages, voxels / self.scaling_factor)
            xy = np.dstack((xx, yy)).reshape(-1, 2)
            z = kde.score_samples(xy).reshape(
                X.shape[0], ages.shape[0])
            zs[:, i, :] = z
        modes = ages[np.argmax(zs, axis=2)]
        return np.mean(modes, axis=1)


@click.command()
@click.argument("input_ages", nargs=1)
@click.argument("train_folder", nargs=1)
@click.argument("test_folder", nargs=1)
def main(input_ages, train_folder, test_folder):
    train_files = glob.glob(os.path.join(train_folder, "*"))
    test_files = glob.glob(os.path.join(test_folder, "*"))
    train = [0] * len(train_files)
    test = [0] * len(test_files)
    ages = np.array(
        [int(age)
         for age in open(input_ages).read().split()])
    for file_name in train_files:
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        # train[i] = np.load(file_name)[0:1000]
        train[i] = np.load(file_name)
    for file_name in test_files:
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        # test[i] = np.load(file_name)[0:1000]
        test[i] = np.load(file_name)
    train = np.array(train)
    test = np.array(test)
    print(train.shape)
    print(test.shape)
    scaling_factor = 15
    kernel = "exponential"
    bandwidth = 15
    estimator = AgeRegressor()
    estimator.fit(train, ages)
    # predicted = estimator.predict(train[0:5, ...])
    # print(np.vstack((ages[0:5], predicted)).T)
    predicted = estimator.predict(test)
    print(predicted)
    # predicted = estimator.predict(test[0:20, ...])
    # print(predicted)
    # predicted = estimator.predict(test[0:40, ...])
    # print(predicted)


if __name__ == "__main__":
    main()
