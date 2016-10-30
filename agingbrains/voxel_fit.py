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


def correlation((i, ar)):
    ar = np.array(list(ar), dtype=float)
    corr = np.abs(np.corrcoef(*ar.T)[0, 1])
    return (i, (corr, ar))


def filter_correlation((i, (corr, ar)), min_correlation=0.4):
    return corr > min_correlation


def estimate_kernel_density(
        (i, ar),
        kernel="exponential",
        bandwidth=15,
        scaling_factor=15):
    ar = np.array(list(ar), dtype=float)
    ar[:, 1] = ar[:, 1] / scaling_factor
    kde = skn.KernelDensity(
        kernel=kernel,
        bandwidth=bandwidth)
    kde.fit(ar)
    return i, kde


def emit_test_voxels((file_name, data)):
    basename = os.path.splitext(os.path.basename(file_name))[0]
    file_id = int(basename.split("_")[1])
    for i, voxel in enumerate(data):
        yield i, (file_id, voxel)


def estimate_age((i, dictionary), scaling_factor=15):
    ages = np.arange(15, 99)
    kde = dictionary["train"][0]
    for file_id, value in dictionary["test"]:
        value = value / scaling_factor
        xy = np.vstack((ages, np.tile(value, ages.shape[0]))).T
        z = kde.score_samples(xy)
        yield file_id, (i, logprobs)
