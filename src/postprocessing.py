import pandas as pd
import argparse
import os
import sys
import re

ROOT = "."


def reformat_string(summary: pd.DataFrame) -> pd.DataFrame:
    summary['taxonomy'] = list(map(lambda x: x.replace('"', "").replace(";", "|"), summary['taxonomy']))
    return summary


def compute_abundances(summary: pd.DataFrame):
    taxonomy = summary['taxonomy']

    # compute relative abundances for each sample column
    summary = summary.drop(columns=["taxonomy"])
    summary = summary.astype(float, errors="ignore")
    total = summary.iloc[0]  # save total counts of abundances

    # save to final data frame
    final = pd.concat([taxonomy, summary.divide(total, axis="columns")], axis=1)

    # remove first row and first column
    final = final.iloc[1:, :]  # remove first row
    final = final.drop(columns=["total"])
    final.rename(columns={'taxonomy': 'subject_id'}, inplace=True)  # rename taxonomy to subject_id, row name

    return final


def reformat_taxonomy(data_dir: str):
    output_dir = f"{ROOT}/intermediate_results"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # iterate through folders in DATA_DIR
    # summary regular expression to fit final.rdp6[number][possible second number].summary
    summary_regex = re.compile(r'final.rdp6\d?\d.summary')
    for body_folder in os.listdir(data_dir):
        for visit_folder in os.listdir(f"{data_dir}/{body_folder}"):
            for input_file in os.listdir(f"{data_dir}/{body_folder}/{visit_folder}"):
                if summary_regex.match(input_file):
                    if "rdp6" in input_file:
                        rdp_classifier = "rdp6"
                    else:
                        rdp_classifier = "rdp18"
                    summary = pd.read_csv(f"{data_dir}/{body_folder}/{visit_folder}/{input_file}", sep='\t')
                    final = compute_abundances(summary)
                    print("%s has %s subjects and %s attributes" % (f"{body_folder}/{visit_folder}/{input_file}",
                                                                    str(final.shape[1]-1), str(final.shape[0])))

                    filename = "intermediate-otus-%s-%s.csv" % (body_folder, visit_folder)
                    output_path = os.path.join(output_dir, body_folder, rdp_classifier, filename)

                    if not os.path.exists(os.path.dirname(output_path)):
                        os.makedirs(os.path.dirname(output_path))

                    final.to_csv(os.path.join(output_dir, body_folder, rdp_classifier, filename), sep='\t', index=False)


def unify_files():
    data_dir = f"{ROOT}/intermediate_results"
    output_dir = f"{ROOT}/final_data"
    tax_dir = f"{ROOT}/taxonomy"

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    if not os.path.exists(tax_dir):
        os.makedirs(tax_dir)

    for body_folder in os.listdir(data_dir):
        print("Creating taxonomy for %s" % body_folder)
        for rdp_folder in os.listdir(f"{data_dir}/{body_folder}"):
            taxonomy_names = []
            for input_file in os.listdir(f"{data_dir}/{body_folder}/{rdp_folder}"):
                current_file = pd.read_csv(os.path.join(data_dir, body_folder, rdp_folder, input_file), sep='\t')
                taxonomy_names.append(current_file["subject_id"])

            taxonomy_names = [cell for row in taxonomy_names for cell in row]
            pd.DataFrame(sorted(set(taxonomy_names))).to_csv(f"{tax_dir}/{body_folder}_{rdp_folder}_taxonomy",
                                                             index=False, header=False)

    print()
    for body_folder in os.listdir(data_dir):
        for rdp_folder in os.listdir(f"{data_dir}/{body_folder}"):
            summary = pd.read_csv(f"{tax_dir}/{body_folder}_{rdp_folder}_taxonomy", header=None, names=["subject_id"])
            for input_file in os.listdir(f"{data_dir}/{body_folder}/{rdp_folder}"):

                if not os.path.exists(os.path.join(output_dir, body_folder, rdp_folder)):
                    os.makedirs(os.path.join(output_dir, body_folder, rdp_folder))

                current_file = os.path.join(data_dir, body_folder, rdp_folder, input_file)
                visit = input_file.split("-")[3].split(".")[0]
                filename = f"otus-{body_folder}-{rdp_folder}-{visit}.pcl"
                print("Changing taxonomy from file %s" % filename)
                current_pd = pd.read_csv(current_file, sep='\t')
                merge = pd.merge(summary, current_pd, how='left', on='subject_id').fillna(0)
                merge.to_csv(os.path.join(output_dir, body_folder, rdp_folder, filename), sep='\t', index=False)
                print("Current file has %s features (taxonomy) and %s subjects" % (merge.shape[0], merge.shape[1]))

# %%
def create_double_visits(dir, body_dir, rdp, output_dir = "double_visits"):
    if not os.path.exists(f"{ROOT}/{output_dir}"):
        os.makedirs(f"{ROOT}/{output_dir}")

    # create files with only TP
    file_prefix = f"otus-{body_dir}-{rdp}-"
    filename = f"{file_prefix}visit1.pcl"
    vis1 = pd.read_csv(os.path.join(dir, body_dir, rdp, filename), sep='\t')
    subjects1 = vis1.columns[1:].to_series()

    vis = pd.read_csv(os.path.join(dir, body_dir, rdp, f"{file_prefix}visit2.pcl"),sep='\t')
    subjects = vis.columns[1:].to_series()
    TP = subjects1[subjects1.isin(subjects)]
    double = vis1[TP]
    double.insert(0, "subject_id", vis1["subject_id"])
    double.to_csv(os.path.join(output_dir, filename), sep='\t',index=False)
    double.to_csv(os.path.join(output_dir, f"{file_prefix}visit2.pcl"), sep='\t', index=False)

# %%
if __name__ == "__main__":
    ROOT = ".."
    reformat_taxonomy(f"{ROOT}/mothur_output/buccal_mucosa_momspi")
    unify_files()

    # get double visits
    for body_dir in os.listdir(f"{ROOT}/final_data"):
        for rdp in os.listdir(f"{ROOT}/final_data/{body_dir}"):
            create_double_visits(f"{ROOT}/final_data", body_dir, rdp)
