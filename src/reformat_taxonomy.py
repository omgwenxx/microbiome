import pandas as pd
import argparse
import os
import sys

"""
We will normalize abundances in order for each column (subject) to sum up to 1. 
"""

# strings for file name and setting
ROOT="."
DATA_DIR = f"{ROOT}/data"
body_site = "feces"
classifier = "rdp6"
project = "moms-pi"
output_folder = "./intermediate_results_%s_%s_%s"%(body_site,project,classifier)

# create folder for intermediate files
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# to redirect console output to text file for analysis
stdout_origin = sys.stdout
text_file = "%s/%s_%s_%s.txt" % (output_folder,body_site,classifier,project)
sys.stdout = open(text_file, "w")

print("Results for %s with %s and project %s" % (body_site,classifier,project))

for i in range(1, 12):
    if classifier == "rdp6":
        input_file = "%s/%s rdp6/visit%s.final.summary" % (DATA_DIR, body_site, i)
    else:
        input_file = "%s/%s rdp18/visit%s.rdp18.summary" % (DATA_DIR, body_site, i)

    try:
        summary = pd.read_csv(input_file, sep='\t')
    except Exception as e:
        print(e)

    # format taxonomy depends on classifier
    if classifier == "rdp6":
        summary['taxonomy'] = list(map(lambda x: x.replace('"', "").replace(";", "|")[5:len(x) - 3], summary['taxonomy']))
    else:
        summary['taxonomy'] = list(map(lambda x: x.replace('"', "").replace(";", "|")[:len(x) - 1], summary['taxonomy']))
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
    print("%s has %s subjects and %s attributes" % (input_file, str(final.shape[0]), str(final.shape[1]-1)))

    filename = "/intermediate-otus-%s-visit%s.csv" % (body_site, i)
    final.to_csv(output_folder + filename, sep='\t', index=False)

# reverts wrinting output to textfile
sys.stdout.close()
sys.stdout=stdout_origin
