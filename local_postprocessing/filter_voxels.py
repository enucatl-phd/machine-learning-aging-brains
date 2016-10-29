import tqdm
import click
import glob
import pandas as pd
import nibabel as nb
import numpy as np



@click.command()
@click.option(
    "--threshold",
    default=0.45,
)
@click.argument(
    "correlations",
    nargs=1,
)
@click.argument(
    "input_files",
    nargs=-1,
)
def main(threshold, correlations, input_files):
    shape = (176, 208, 176)
    corr_data_frame = pd.read_csv(correlations, header=None)
    correlation_brain = np.zeros(shape=shape[0] * shape[1] * shape[2], dtype=float)
    for row in corr_data_frame.itertuples():
        correlation = row[2]
        if correlation > threshold:
            correlation_brain[row[1]] = row[2]
    for file_name in tqdm.tqdm(input_files):
        data = nb.load(file_name).get_data().flatten()
        filtered_data = data[correlation_brain > 0]
        output_name = file_name.replace(
            "set_", "filtered_set_").replace(
                ".nii", ".csv")
        np.save(output_name, filtered_data)

if __name__ == "__main__":
    main()
