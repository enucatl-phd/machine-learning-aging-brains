import numpy as np


def global_thresholding((file_name, data)):
    csf = np.size(data[np.logical_and(data > 0, data < 300)])
    gm = np.size(data[np.logical_and(data > 650, data < 850)])
    wm = np.size(data[np.logical_and(data > 1250, data < 1450)])
    return (file_name, (csf, gm, wm))
