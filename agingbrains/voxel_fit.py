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
    age = dictionary["gender"][0]
    for i, voxel in enumerate(data):
        if voxel > 0:
            yield i, (age, voxel)


def correlation((i, ar)):
    ar = np.array(list(ar), dtype=float)
    corr = np.abs(np.corrcoef(*ar.T)[0, 1])
    return (i, (corr, ar))


def fisher_score((i, ar)):
    ar = np.array(list(ar), dtype=int)
    genders, values = ar.T
    fisher = (
        (np.median(values[genders == 0])
        - np.median(values[genders == 1])) ** 2 / 
        (np.std(values[genders == 0]) + np.std(values[genders == 1]))
    )
    return (i, (fisher, ar))
