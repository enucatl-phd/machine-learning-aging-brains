import click
import nibabel as nb
import numpy as np
import csv
import skimage.segmentation as sks
from progress_bar import progress_bar


@click.command()
@click.argument(
    "output_file",
    type=click.File("w"),
    nargs=1)
@click.argument(
    "input_files",
    type=click.Path(exists=True),
    nargs=-1)
def main(output_file, input_files):
    writer = csv.writer(output_file)
    writer.writerow(["id", "empty", "csf", "gm", "wm"])
    n = len(input_files)
    for i, file_name in enumerate(input_files):
        img = nb.load(file_name).get_data()[..., 0]
        empty = np.size(img[img == 0])
        markers = np.zeros(img.shape, dtype=np.uint8)
        sample_id = file_name.split(".")[0].split("_")[2]
        markers[img == 0] = 1
        markers[np.logical_and(img > 0, img < 300)] = 2
        markers[np.logical_and(img > 650, img < 850)] = 3
        markers[np.logical_and(img > 1250, img < 1450)] = 4
        labels = sks.random_walker(img, markers, beta=60, mode="cg_mg")
        segmentation_file_name = file_name.replace(
            "train", "train_segmented").replace(
                ".nii", ".npy")
        np.save(segmentation_file_name, labels)
        print(progress_bar((i + 1) / n), end="")
        writer.writerow(
            [
                sample_id,
                np.size(labels[labels == 1]),
                np.size(labels[labels == 2]),
                np.size(labels[labels == 3]),
                np.size(labels[labels == 4])
            ]
        )
    print()

if __name__ == "__main__":
    main()
