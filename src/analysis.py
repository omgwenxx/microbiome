import os
import re

import pandas as pd

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

    # if metadata folder does not exist, make folder
    if not os.path.exists(f"{ROOT}/metadata"):
        os.mkdir(f"{ROOT}/metadata")

    # Count visits per sample and body_site
    visits_lists = metadata[["subject_id", "sample_body_site", "visit_number"]].groupby(
        ["subject_id", "sample_body_site"]).agg(list)
    visits_lists.to_csv(f"{ROOT}/metadata/visits.csv")
    print("Save visit file to ", f"{ROOT}/metadata/visits.csv")


def get_multiple_sites(input_dir="./hmp_portal_files") -> None:
    """
    Saves a file that includes subjects that have fist and second visit information to the set of body sites
    :param input_dir: 
    :return: 
    """
    metadata = get_metadata(input_dir)

    # if metadata folder does not exist, make folder
    if not os.path.exists(f"{ROOT}/metadata"):
        os.mkdir(f"{ROOT}/metadata")

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


def print_non_zero_rows(file: str) -> None:
    """
    prints a dataframe with the non-zero rows of a file
    this can only be run with postprocessed files
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
    print(f"total {total} columns {len(df.columns)}")
    print("Average:", round(total / (len(df.columns) - 1)))


def create_merge_bodysites_files(input_dir: str = "final_data"):
    # check if file exists
    if not os.path.exists(f"{ROOT}/metadata/multiple_sites.csv"):
        get_multiple_sites()

    multi_sites = pd.read_csv("metadata/multiple_sites.csv")
    multi_sites = multi_sites[multi_sites["sample_body_site"] == "{'vagina', 'rectum', 'buccal mucosa'}"]
    multi_sites_ids = multi_sites["subject_id"]

    rdp6_df1 = pd.DataFrame(multi_sites["subject_id"])
    rdp18_df1 = pd.DataFrame(multi_sites["subject_id"])
    rdp6_df2 = pd.DataFrame(multi_sites["subject_id"])
    rdp18_df2 = pd.DataFrame(multi_sites["subject_id"])

    folder_names = ['rectum_momspi', 'buccal_mucosa_momspi', 'vagina_momspi']
    for body_dir in os.listdir(input_dir):
        if body_dir in folder_names:
            print(f"\n{body_dir} ###########################")
            for rdp in os.listdir(os.path.join(input_dir, body_dir)):
                for file in os.listdir(os.path.join(input_dir, body_dir, rdp)):
                    if file.endswith("visit1.pcl") or file.endswith("visit2.pcl"):
                        filename = os.path.join(input_dir, body_dir, rdp, file)
                        df = pd.read_csv(filename, sep="\t").transpose()  # transpose so rows are subjects

                        df = df.reset_index()
                        new_header = df.iloc[0]  # grab the first row for the header
                        df = df[1:]  # take the data less the header row
                        df.columns = new_header  # set the header row as the df header

                        filtered_df = df[df["subject_id"].isin(multi_sites_ids)]
                        print(filtered_df.shape)

                        # add suffix of body_site except for subject_id
                        keep_same = {'subject_id'}
                        filtered_df.columns = ['{}{}'.format(c, '' if c in keep_same else f"{body_dir}") for c in
                                               filtered_df.columns]

                        if rdp == "rdp6" and file.endswith("visit1.pcl"):
                            rdp6_df1 = pd.merge(rdp6_df1, filtered_df, on="subject_id")
                        if rdp == "rdp18" and file.endswith("visit1.pcl"):
                            rdp18_df1 = pd.merge(rdp18_df1, filtered_df, on="subject_id")
                        if rdp == "rdp6" and file.endswith("visit2.pcl"):
                            rdp6_df2 = pd.merge(rdp6_df2, filtered_df, on="subject_id")
                        if rdp == "rdp18" and file.endswith("visit2.pcl"):
                            rdp18_df2 = pd.merge(rdp18_df2, filtered_df, on="subject_id")

    body_site = "rectum_buccal_muccosa_vagina"
    output_dir = f"{ROOT}/merge_data/rectum_buccal-muccosa_vagina"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        os.makedirs(f"{output_dir}/rdp6")
        os.makedirs(f"{output_dir}/rdp18")

    rdp6_df1.transpose().to_csv(f"{output_dir}/rdp6/otus-{body_site}-rdp6-visit1.pcl", sep='\t', header=False)
    rdp18_df1.transpose().to_csv(f"{output_dir}/rdp18/otus-{body_site}-rdp18-visit1.pcl", sep='\t', header=False)
    rdp6_df2.transpose().to_csv(f"{output_dir}/rdp6/otus-{body_site}-rdp6-visit2.pcl", sep='\t', header=False)
    rdp18_df2.transpose().to_csv(f"{output_dir}/rdp18/otus-{body_site}-rdp18-visit2.pcl", sep='\t', header=False)


if __name__ == "__main__":
    ROOT = ".."
    dir = f"{ROOT}/final_data_compare"
    for body_dir in os.listdir(dir):
        print(f"\n{body_dir} ###########################")
        for rdp in os.listdir(os.path.join(dir, body_dir)):
            print(f"\nAverage non zero rows for {rdp}")
            for file in os.listdir(os.path.join(dir, body_dir, rdp)):
                filepath = os.path.join(dir, body_dir, rdp, file)
                print(file.split("-")[-1], end=" ")
