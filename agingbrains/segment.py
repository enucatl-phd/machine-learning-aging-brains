import nibabel as nb

def main(file_name):
    img = nb.load(file_name).get_data()[..., 0]
    markers = np.zeros(img.shape, dtype=np.uint8)
    markers[img == 0] = 1  # empty
    markers[np.logical_and(img > 0, img < 300)] = 2  # csf
    markers[np.logical_and(img > 650, img < 850)] = 3  # gm
    markers[np.logical_and(img > 1250, img < 1450)] = 4  # wm
