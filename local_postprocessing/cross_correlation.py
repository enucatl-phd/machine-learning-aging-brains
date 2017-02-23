import numpy as np
import click
import os


@click.command()
@click.argument("input_files", nargs=-1)
def main(input_files):
    voxels = [0] * len(input_files)
    for file_name in input_files:
        data = np.load(file_name)
        basename = os.path.splitext(os.path.basename(file_name))[0]
        i = int(basename.split("_")[1]) - 1
        voxels[i] = data[:1000]
    voxels = np.array(voxels)
    corr = np.corrcoef(voxels, rowvar=False)
    triu = np.triu(corr) - np.eye(corr.shape[0])
    print(np.sum(np.all(triu < 0.3, axis=1)))

if __name__ == "__main__":
    main()
