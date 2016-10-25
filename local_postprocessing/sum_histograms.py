from __future__ import print_function

import click
import nibabel as nb
import numpy as np
import csv
from tqdm import tqdm

        
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
    histograms = []
    bin_edges = []
    writer = csv.writer(output_file)
    writer.writerow(["bin", "voxels"])
    n = len(input_files)
    for file_name in tqdm(input_files):
        img = nb.load(file_name).get_data()[..., 0]
        img = img[img > 0]  # remove black voxels
        histogram, bin_edges = np.histogram(
            img.flatten(),
            bins=600,
            range=(0, 3000)
        )
        histograms.append(histogram)
    summed = np.sum(np.array(histograms), axis=0)
    for bin_edge, voxel_sum in zip(bin_edges, summed):
        writer.writerow([bin_edge, voxel_sum])
    print()

if __name__ == "__main__":
    main()
