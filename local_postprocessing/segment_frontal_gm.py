import nibabel as nb
import numpy as np
import tqdm
import click


@click.command()
@click.argument("input_files", nargs=-1)
def main(input_files):
    for file_name in tqdm.tqdm(input_files):
        output_file = file_name.replace(
            "set_", "frontal_thresholding_set_").replace(
                ".nii", ".csv")
        data = nb.load(file_name).dataobj[10:160, 110:190, 45:160]
        gm = np.size(data[np.logical_and(data > 650, data < 850)]) 
        with open(output_file, "w") as outfile:
            outfile.write(str(gm))

if __name__ == "__main__":
    main()
