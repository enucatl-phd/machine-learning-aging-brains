import numpy as np
import sklearn.gaussian_process as skg


def emit_voxels((file_name, dictionary)):
    data = dictionary["data"][0][..., 0]
    age = dictionary["age"][0]
    for x in range(data.shape[0]):
        for y in range(data.shape[1]):
            for z in range(data.shape[2]):
                yield ((x, y, z), (age, data[x, y, z]))


def filter_empty(((x, y, z), ar)):
    ar = np.array(ar)
    if np.any(ar[:, 1]):
        yield ((x, y, z), ar)


def fit_voxel(((x, y, z), ar)):
    ages, voxels = ar.T
    kernel = (
        skg.kernels.ConstantKernel(constant_value=500, constant_value_bounds=(100, 2000))
        * skg.kernels.RBF(length_scale=5, length_scale_bounds=(3, 200))
        + skg.kernels.WhiteKernel(noise_level=1000, noise_level_bounds=(1e3, 1e4))
    )
    gp = skg.GaussianProcessRegressor(kernel=kernel, n_restarts_optimizer=9)
    gp.fit(ages.reshape(-1, 1), voxels)
    aging_scale = gp.kernel_.get_params()['k1__k2__length_scale']
    return ((x, y, z), aging_scale)
