import click
import nibabel as nb
import numpy as np
import csv
import skimage.segmentation as sks


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
    writer.writerow(["bin", "empty", "csf", "gm", "wm"])
    n = len(input_files)
    for i, file_name in enumerate(input_files):
        img = nb.load(file_name).get_data()[..., 0]
        empty = len(img[img == 0].flatten())
        markers = np.zeros_like(img)
        markers[np.logical_and(img > 0, img < 300)] = 1
        markers[np.logical_and(img > 650, img < 850)] = 2
        markers[np.logical_and(img > 1250, img < 1450)] = 3
        labels = sks.random_walker(img, markers, beta=10, mode="cg_mg")
        print(labels.shape)
        print(progress_bar((i + 1) / n), end="")
    print()

if __name__ == "__main__":
    main()
