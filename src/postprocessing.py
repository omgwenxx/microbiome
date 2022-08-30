import pandas as pd
import argparse
import os
import sys
import re

ROOT = "."


def reformat_taxonomy():
    DATA_DIR = f"{ROOT}/mothur_output"
    OUTPUT_DIR = f"{ROOT}/intermediate_results"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    def compute_abundances(summary: pd.DataFrame):
        taxonomy = summary['taxonomy']

        # compute relative abundances for each sample column
        summary = summary.drop(columns=["taxonomy"])
        summary = summary.astype(float, errors="ignore")
        total = summary.iloc[0]  # save total counts of abundances

        # save to final data frame
        final = pd.concat([taxonomy, summary.divide(total, axis="columns").round(9)], axis=1)

        # remove first row and first column
        final = final.iloc[1:, :]  # remove first row
        final = final.drop(columns=["total"])
        final.rename(columns={'taxonomy': 'subject_id'}, inplace=True)  # rename taxonomy to subject_id, row name

        return final

    def reformat_string(summary: pd.DataFrame) -> pd.DataFrame:
        summary['taxonomy'] = list(map(lambda x: x.replace('"', "").replace(";", "|"), summary['taxonomy']))
        return summary

    # iterate through folders in DATA_DIR
    # summary regular expression to fit final.rdp[number][possible second number].summary
    summary_regex = re.compile(r'final.rdp\d?\d.summary')
    for body_folder in os.listdir(DATA_DIR):
        for visit_folder in os.listdir(f"{DATA_DIR}/{body_folder}"):
            for input_file in os.listdir(f"{DATA_DIR}/{body_folder}/{visit_folder}"):
                if summary_regex.match(input_file):
                    if "rdp6" in input_file:
                        rdp_classifier = "rdp6"
                    else:
                        rdp_classifier = "rdp18"
                    summary = pd.read_csv(f"{DATA_DIR}/{body_folder}/{visit_folder}/{input_file}", sep='\t')
                    summary = reformat_string(summary, rdp_classifier)
                    final = compute_abundances(summary)
                    print("%s has %s subjects and %s attributes" % (f"{body_folder}/{visit_folder}/{input_file}",
                                                                    str(final.shape[1]), str(final.shape[0] - 1)))

                    filename = "intermediate-otus-%s-%s.csv" % (body_folder, visit_folder)
                    output_path = os.path.join(OUTPUT_DIR, body_folder, rdp_classifier, filename)

                    if not os.path.exists(os.path.dirname(output_path)):
                        os.makedirs(os.path.dirname(output_path))

                    final.to_csv(os.path.join(OUTPUT_DIR, body_folder, rdp_classifier, filename), sep='\t', index=False)


def unify_files():
    DATA_DIR = f"{ROOT}/intermediate_results"
    OUTPUT_DIR = f"{ROOT}/final_data_OTU"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for body_folder in os.listdir(DATA_DIR):
        for rdp_folder in os.listdir(f"{DATA_DIR}/{body_folder}"):
            taxonomy_names = []
            for input_file in os.listdir(f"{DATA_DIR}/{body_folder}/{rdp_folder}"):
                print("Adding axonomy from file %s" % (os.path.join(body_folder, rdp_folder, input_file)))
                current_file = pd.read_csv(os.path.join(DATA_DIR, body_folder, rdp_folder, input_file), sep='\t')
                taxonomy_names.append(current_file["subject_id"])

    taxonomy_names = [cell for row in taxonomy_names for cell in row]
    pd.DataFrame(sorted(set(taxonomy_names))).to_csv("unique_taxonomy", index=False, header=False)
    summary = pd.read_csv("unique_taxonomy", header=None, names=["subject_id"])

    for body_folder in os.listdir(DATA_DIR):
        for rdp_folder in os.listdir(f"{DATA_DIR}/{body_folder}"):
            for input_file in os.listdir(f"{DATA_DIR}/{body_folder}/{rdp_folder}"):

                if not os.path.exists(os.path.join(OUTPUT_DIR, body_folder, rdp_folder)):
                    os.makedirs(os.path.join(OUTPUT_DIR, body_folder, rdp_folder))

                current_file = os.path.join(DATA_DIR, body_folder, rdp_folder, input_file)
                filename = "final-otus-%s-%s-%s.pcl" % (body_folder, rdp_folder, input_file.split("-")[3])
                print("Changing taxonomy from file %s" % current_file)
                current_pd = pd.read_csv(current_file, sep='\t')
                merge = pd.merge(summary, current_pd, how='left', on='subject_id').fillna(0)
                merge.to_csv(os.path.join(OUTPUT_DIR, body_folder, rdp_folder, filename), sep='\t', index=False)
                print("Current file has %s rows and %s columns" % (merge.shape[0], merge.shape[1]))


if __name__ == "__main__":
    ROOT = ".."
    # write code here for testing functions
