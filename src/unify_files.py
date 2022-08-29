import pandas as pd
import argparse
import os

"""
This script is unify the output files from mothur. Each file from mothur only shows the abundance
for the data samples that were processed. Therefore different visits have different number of features (hierachy steps).
The script takes the different visit files as input and stores all hierarchy steps in a file unique_taxonomy. Then the 
feature range of each file is unified by filling in missing hierachy features.

CAUTION: Less samples per visit lead to less abundances detected.

Additional string preprocessing is done 
in order for the final file to look like the original files from Franzosa et al. e.g. processing the taxonomy name
structure.
"""

# save strings for file name
body_site = "feces"
classifier = "rdp6"
project = "moms-pi"
input_dir = "../rdp6_postprocessing/"
visit = "visit1"
filename = "otus-%s-%s.pcl" % (body_site, visit)
INPUT_DIR= "intermediate_results_%s_%s_%s" % (body_site,project,classifier)
OUTPUT_DIR= "./data_processed/%s_%s_%s"%(body_site,project,classifier)

# create folder for unified files
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

taxonomy_names = []

for i in range(1, 12):
    current_file = pd.read_csv("visit%s.final.summary" % (i), sep='\t')
    print("Adding Taxonomy from file visit%s.final.summary" % (i))
    taxonomy_names.append(current_file["taxonomy"])

taxonomy_names = [cell for row in taxonomy_names for cell in row]
pd.DataFrame(sorted(set(taxonomy_names))).to_csv("unique_taxonomy", index=False, header=False)

summary = pd.read_csv("unique_taxonomy", header=None, names=["taxonomy"])

for i in range(1,12):
    print("Processing visit%s.final.summary"%(i))
    current_file = pd.read_csv("visit%s.final.summary"%(i), sep='\t')
    merged_file = pd.merge(summary, current_file, how = 'left', on = 'taxonomy').fillna(0)
    merged_file.to_csv("%s/visit%s.final.summary"%(folder_name,i), sep = '\t', index=False)
    print("Current file has %s rows and %s columns"%(merged_file.shape[0],merged_file.shape[1]))