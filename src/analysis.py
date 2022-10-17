import pandas as pd
import csv
import pandas as pd
import re
import os

ROOT = "."


def get_metadata(input_dir="./hmp_portal_files") -> pd.DataFrame:
    """
    Returns a dataframe with the metadata of the samples from all metadata files within a directory with multiple
    directories of hmp metadata files
    :param input_dir: folder with subfolders
    :return: dataframe of merged metadata
    """
    print("Get visit information...")
    metadata_regex = re.compile(r'hmp_manifest_metadata_(.*).tsv')  # match hmp_manifest_metadata_*.tsv files
    metadata = pd.DataFrame()
    for body_dir in os.listdir(input_dir):
        for file in os.listdir(os.path.join(input_dir, body_dir)):
            if metadata_regex.match(file):
                meta_file = os.path.join(input_dir, body_dir, file)
                metadata = pd.concat([pd.read_csv(meta_file, sep='\t'), metadata], axis=0)

    return metadata


def get_visits(input_dir="./hmp_portal_files") -> None:
    """
    Saves a csv file with the body site and sample and a list of visits
    :param input_dir:
    :return:
    """

    metadata = get_metadata(input_dir)

    # Count visits per sample and body_site
    visits_lists = metadata[["subject_id", "sample_body_site", "visit_number"]].groupby(
        ["subject_id", "sample_body_site"]).agg(list)
    visits_lists.to_csv(f"{ROOT}/metadata/visits.csv")


def get_multiple_sites(input_dir="./hmp_portal_files") -> None:
    """
    Saves a file that includes subjects that have fist and second visit information to the set of body sites
    :param input_dir: 
    :return: 
    """
    metadata = get_metadata(input_dir)
    # Get subjects with multiple body_sites in the first two visits
    vis12 = metadata[metadata["visit_number"] < 3]
    body_sites = vis12[["subject_id", "sample_body_site", "visit_number"]]
    body_sites.iloc[:, 1:2] = body_sites.iloc[:, 1:2].applymap(lambda x: {x})
    # returs df with all body sites per sample and visit
    body_sites = body_sites.groupby(["subject_id", "visit_number"]).agg(
        lambda x: set.union(*x)).reset_index()  # returs df with all body sites per sample and visit
    # returns df that has subjects id that have all body sites for visit 1 and 2
    final = body_sites[["subject_id", "sample_body_site"]].groupby(["subject_id"]).agg(lambda x: set.intersection(*x))
    final.to_csv(f"{ROOT}/metadata/multiple_sites.csv")


def print_info(dir: str):
    """
    Prints the number of subjects and features for each file in a directory, which represents a body site and visit using
    either rdp6 or rdp18 for classification
    :param dir:
    :return:
    """
    for body_dir in os.listdir(dir):
        print(f"\n{body_dir} ###########################")
        for visit in os.listdir(os.path.join(dir, body_dir)):
            print(visit)
            for file in os.listdir(os.path.join(dir, body_dir, visit)):
                if len(file.split(".")) == 2:
                    continue
                print(file.split(".")[1], end=" ")
                df = pd.read_csv(os.path.join(dir, body_dir, visit, file), sep='\t')
                # -2 subjects because of taxonomy and total
                # -1 feature because of root
                print(f"{df.shape[1] - 2} Subjects and {df.shape[0] - 1} Features")


def print_ground_truth(dir, body_dir, rdp: str = "rdp6", visit: str = "visit1") -> None:
    """
    Prints the number of True Positives (samples in visit file also appear in the printed file) and True Negatives
    (sample does not appear in printed file) for each file in a body directory (always using rdp6 per default).
    :param body_dir: folder containing the rdp6 and rdp18 folder (after using postprocessing step in pipeline)
    :param dir: folder with subfolder of body sites
    :return:
    """
    print(f"\n{body_dir} ###########################")
    filename = f"otus-{body_dir}-{rdp}-{visit}.pcl"
    vis1 = pd.read_csv(os.path.join(dir, body_dir, rdp, filename), sep='\t')
    subjects1 = vis1.columns[1:].to_series()
    print("Total of subjects in visit 1:", subjects1.count())
    for file in os.listdir(os.path.join(dir, body_dir, rdp)):
        if file.endswith(f"{visit}.pcl"):
            continue
        vis = pd.read_csv(os.path.join(dir, body_dir, rdp, file), sep='\t')
        subjects = vis.columns[1:].to_series()
        TP = subjects1[subjects1.isin(subjects)]
        # get number of subjects that are not in subjects1
        TN = subjects[~subjects.isin(subjects1)]
        print(f"Total of subjects in {file.split('-')[-1]}:", subjects.count())
        print(f"{body_dir} {file.split('-')[-1]} - TP {len(TP)} TN {len(TN)}\n")
# possible call of get_ground_truth function
# dir = "final_data"
# for body_dir in os.listdir("final_data"):
#    print_ground_truth(dir, body_dir)


def print_non_zero_rows(file: str) -> None:
    """
    prints a dataframe with the non-zero rows of a file
    :param file: path to file to be read in as DataFrame
    :return:
    """
    # get non-zero values per column
    df = pd.read_csv(file, sep='\t')
    total = 0
    for column_name in df.columns:
        column = df[column_name]
        # Get the count of non-Zeros values in column
        count_of_non_zeros = (column != 0).sum()
        total += count_of_non_zeros

    print("Average:", round(total / (len(df.columns) - 1)))

if __name__ == "__main__":
    dir = "final_data"
    for body_dir in os.listdir("final_data"):
        print(f"\n{body_dir} ###########################")
        for rdp in os.listdir(os.path.join(dir, body_dir)):
            print(f"\nAverage non zero rows for {rdp}")
            for file in os.listdir(os.path.join(dir, body_dir, rdp)):
                filepath = os.path.join(dir, body_dir, rdp, file)
                print(file.split("-")[-1], end=" ")
                print_non_zero_rows(filepath)
