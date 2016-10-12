import nibabel as nb

print(
    nb.load("data/set_train/train_100.nii").get_data()[70, 100, 70, 0])
print(
    nb.load("data/set_train/train_101.nii").get_data()[70, 100, 70, 0])
