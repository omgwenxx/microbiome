import os
import re

import pandas as pd

ROOT = "."


def merge_files(input_dir):
    """
    This method merges the download .tsv file with the metadata .tsv file by sample id.
    Saves it into a file called total_info.tsv if not named otherwise
    """

    print("Merging files...")
    metadata_regex = re.compile(r'hmp_manifest_metadata_(.*).tsv')  # match hmp_manifest_metadata_*.tsv files
    download_regex = re.compile(r'hmp_manifest_(?!metadata)')  # match hmp_manifest_*.tsv files

    meta_file = ""
    download_file = ""

    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if metadata_regex.match(file):
                meta_file = os.path.join(root, file)
            if download_regex.match(file):
                download_file = os.path.join(root, file)

    download_info = pd.read_csv(download_file, sep='\t')
    metadata = pd.read_csv(meta_file, sep='\t').drop_duplicates()
    total = pd.merge(metadata, download_info, validate="one_to_many", on="sample_id")
    print("Body sites included in the dataset: %s" % (str(total["sample_body_site"].unique())))

    # puts subject id as first column
    subject_ids = total['subject_id']
    total = total.drop(columns=['subject_id'])
    total.insert(loc=0, column='subject_id', value=subject_ids)
    total.to_csv(f"{ROOT}/total_info.tsv", index=False)
    return total


def create_folders():
    """
    Creates folder structure for the final .tsv files
    """
    downloaddir = f"{ROOT}/download"
    metadatadir = f"{ROOT}/metadata"

    # create folders for download and metadata files
    if not os.path.isdir(downloaddir):
        os.makedirs(downloaddir)
        print("Created folder : ", downloaddir)

    if not os.path.isdir(metadatadir):
        os.makedirs(metadatadir)
        print("Created folder : ", metadatadir)

    # extract body sites and study names
    total = pd.read_csv(f"{ROOT}/total_info.tsv")
    body_sites = total['sample_body_site'].unique()
    study_names = total['study_full_name'].unique()

    # create folder for files
    for body_site in body_sites:
        for study_name in study_names:
            if study_name == "Inflammatory Bowel Disease Multi-omics Database (IBDMDB)":
                study_name = "ibdmbd"
            else:
                study_name = study_name.replace(" ", "_")
            body_site = body_site.replace(" ", "_")
            filedir = f"{downloaddir}/{body_site}_{study_name}"
            metafiledir = f"{metadatadir}/{body_site}_{study_name}_metadata"

            if not os.path.isdir(filedir):
                os.makedirs(filedir)
                print("Created folder : ", filedir)

            if not os.path.isdir(metafiledir):
                os.makedirs(metafiledir)
                print("Created folder : ", metafiledir)


def export_all(num_visit: int):
    """
    Exports all visits separately for each body site. The final .tsv files are saved in folders
    with names ./download/<body_site>_<study_name> and ./metadata/<body_site>_<body_site>_<study_name>_metadata
    :param num_visit: number of visits to extract, all visits <= numvisit are exported
    """

    total = pd.read_csv(f"{ROOT}/total_info.tsv")
    downloaddir = f"{ROOT}/download"
    metadatadir = f"{ROOT}/metadata"

    # extract body sites and study names
    body_sites = total['sample_body_site'].unique()
    study_names = total['study_full_name'].unique()
    all_visits = total['visit_number'].unique()
    visits = list(filter(lambda score: score <= num_visit, all_visits))  # filter all visits smaller than numvisit

    for body_site in body_sites:
        for study_name in study_names:
            body_site = body_site.replace(" ", "_")

            # save files with correct name formatting
            if study_name == "Inflammatory Bowel Disease Multi-omics Database (IBDMDB)":
                study_dir_name = "ibdmbd"
            else:
                study_dir_name = study_name.replace(" ", "_")

            filedir = f"{downloaddir}/{body_site}_{study_dir_name}"
            metafiledir = f"{metadatadir}/{body_site}_{study_dir_name}_metadata"

            # create dataframe for each visit
            for visit in visits:
                print(f"Creating files for {body_site} from {study_name} visit {visit}")
                filtered = total[(total['visit_number'] == visit)
                                 & (total['sample_body_site'] == body_site.replace("_", " "))
                                 & (total['study_full_name'] == study_name)]
                download = filtered[["file_id", "md5", "size", "urls", "sample_id", "subject_id"]]
                metadata = filtered[["sample_id", "sample_body_site", "study_full_name", "visit_number", "subject_id"]]

                download_file_name = f"{filedir}/visit{visit}.tsv"
                metadata_file_name = f"{metafiledir}/visit{visit}_metadata.tsv"
                download.to_csv(download_file_name, sep='\t', index=False)
                metadata.to_csv(metadata_file_name, sep='\t', index=False)
