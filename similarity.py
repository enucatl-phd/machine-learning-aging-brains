import click
import nibabel as nb
import numpy as np
import csv
import itertools
import skimage.measure as skm
from progress_bar import progress_bar
from id_from_filename import id_from_filename, age_from_id


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
    writer.writerow(
        [
            "id1",
            "id2",
            "age1",
            "age2",
            "ssim3", 
            "ssim5", 
            "mse"
        ])
    pairs = list(itertools.combinations(input_files, 2))
    n = len(pairs)
    print(n)
    for pair in pairs:
        pair
    for i, (file_name1, file_name2) in enumerate(pairs):
        img1 = nb.load(file_name1).get_data()[..., 0]
        img2 = nb.load(file_name2).get_data()[..., 0]
        id1 = id_from_filename(file_name1)
        id2 = id_from_filename(file_name2)
        ssim3 = skm.compare_ssim(img1, img2, win_size=3, dynamic_range=3000)
        ssim5 = skm.compare_ssim(img1, img2, win_size=5, dynamic_range=3000)
        mse = skm.compare_mse(img1, img2)
        age1 = age_from_id(id1)
        age2 = age_from_id(id2)
        print(progress_bar((i + 1) / n), end="")
        writer.writerow(
            [id1, id2, age1, age2, ssim3, ssim5, mse]
        )
    print()

if __name__ == "__main__":
    main()
