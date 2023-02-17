This folder contains data in its final form to be processed be the idability framework. Meaning it is provided in a .pcl
format where columns are subjects/samples and rows represent the relative abundance (per sample) of OTU.

The folder structure provided looks like the following:
```
data
└───<body-site_study-name>
    └───rdp6
    |   otus-<body-site_study-name>-rdp6-visit1.pcl
    |   otus-<body-site_study-name>-rdp6-visit2.pcl
    |   otus-<body-site_study-name>-rdp6-visit3.pcl
    |   ...
    └───rdp18
    |   otus-<body-site_study-name>-rdp18-visit1.pcl
    |   otus-<body-site_study-name>-rdp18-visit2.pcl
    |   otus-<body-site_study-name>-rdp18-visit3.pcl
    |   ...
```

We are providing different formats for experiments:
- `final_data`: Extracted taxonomies for each body site and using rdp6 and rdp18 taxomies for classifications. Files contain all samples that were provided (not only visits that appear in all visits). Those files were created using the high-trim data with a cutoff of 80.
- `double_visits`: Compared to the `final_data` folder this folder only contains files with samples that are present in the first visit and a consecutive second visit. This is equal to the files that were used in the Franzosa et al. paper.
- `low_trim_data`