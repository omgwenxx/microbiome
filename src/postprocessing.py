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

    def reformat_string(summary: pd.DataFrame, rdp_classifier: str) -> pd.DataFrame:
        if rdp_classifier == "rdp6":
            summary['taxonomy'] = list(
                map(lambda x: x.replace('"', "").replace(";", "|")[5:len(x) - 3], summary['taxonomy']))
        else:
            summary['taxonomy'] = list(
                map(lambda x: x.replace('"', "").replace(";", "|")[:len(x) - 1], summary['taxonomy']))
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
                    output_path = os.path.join(OUTPUT_DIR,body_folder,rdp_classifier,filename)

                    if not os.path.exists(os.path.dirname(output_path)):
                        os.makedirs(os.path.dirname(output_path))

                    final.to_csv(os.path.join(OUTPUT_DIR,body_folder,rdp_classifier,filename), sep='\t', index=False)

if __name__ == "__main__":
    ROOT = ".."
