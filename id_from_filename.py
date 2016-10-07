def id_from_filename(file_name):
    return int(file_name.split(".")[0].split("_")[2])


def age_from_id(sample_id):
    with open("data/targets.csv") as age_file:
        return int(age_file.readlines()[sample_id])
