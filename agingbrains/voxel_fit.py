from __future__ import division, print_function
import os
import logging
import numpy as np

import sklearn
logging.info("SKLEARN VERSION %s", sklearn.__version__)

import sklearn.gaussian_process as skg
import sklearn.gaussian_process.kernels as skgk
import sklearn.neighbors as skn


def emit_voxels((file_name, dictionary)):
    data = dictionary["data"][0].flatten()
    age = dictionary["age"][0]
    for i, voxel in enumerate(data):
        if voxel > 0:
            yield i, (age, voxel)


def filter_voxels_correlation((i, ar), correlation_threshold=0.4):
    ar = np.array(list(ar), dtype=float)
    corr = np.abs(np.corrcoef(*ar.T)[0, 1])
    if corr > correlation_threshold:
        yield (i, (corr, ar))


def filter_voxels_gaussian_process((i, ar), aging_scale_threshold=80):
    ar = np.array(list(ar), dtype=float)
    ages, voxels = ar.T
    corr = np.abs(np.corrcoef(*ar.T)[0, 1])
    kernel = (
        skgk.ConstantKernel(constant_value=500, constant_value_bounds=(100, 2000))
        * skgk.RBF(length_scale=5, length_scale_bounds=(3, 200))
        + skgk.WhiteKernel(noise_level=1000, noise_level_bounds=(1e3, 1e4))
    )
    gp = skg.GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
    gp.fit(ages.reshape(-1, 1), voxels)
    aging_scale = gp.kernel_.get_params()['k1__k2__length_scale']
    if aging_scale < aging_scale_threshold:
        yield (i, (aging_scale, ar))


def estimate_kernel_density(
        (i, (aging_scale, ar)),
        kernel="exponential",
        bandwidth=15,
        scaling_factor=15):
    ar[:, 1] = ar[:, 1] / scaling_factor
    kde = skn.KernelDensity(
        kernel=kernel,
        bandwidth=bandwidth)
    kde.fit(ar)
    return i, kde


def emit_test_voxels((file_name, data)):
    data = data.flatten()
    basename = os.path.splitext(os.path.basename(file_name))[0]
    file_id = int(basename.split("_")[1])
    for i, voxel in enumerate(data):
        if voxel > 0:
            yield i, (file_id, voxel)


def filter_test_voxels((i, dictionary)):
    return dictionary["train"]


def estimate_age((i, dictionary), scaling_factor=15):
    ages = np.arange(15, 99)
    kde = dictionary["train"][0]
    for file_id, value in dictionary["test"]:
        value = value / scaling_factor
        xy = np.vstack((ages, np.tile(value, ages.shape[0]))).T
        z = np.exp(kde.score_samples(xy))
        xy[:, 1] = z / np.sum(z)
        mode = xy[np.argmax(xy[:, 1]), 0]
        yield file_id, mode


def average_age((file_id, modes)):
    final_age_estimate = np.mean(np.array(list(modes)))
    return file_id, final_age_estimate
