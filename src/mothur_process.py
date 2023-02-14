import json
import os

import requests
from mothur_py import Mothur

from src.util import *

ROOT = "."


def get_mothur() -> Mothur:
    """
    Create mothur wrapper object based on os system
    :return: Mothur object
    """
    if check_os() == "Windows":
        print("You are operating on Windows.")

        # check if mothur folder exists
        if not os.path.isfile(f"{ROOT}/src/Mothur.win.zip"):
            print("Downloading Mothur...")
            url = "https://github.com/mothur/mothur/releases/download/v1.46.0/Mothur.win.zip"
            r = requests.get(url)
            with open(f"{ROOT}/src/Mothur.win.zip", 'wb') as f:
                f.write(r.content)
            print("Download complete.")
            unpack_zip(f"{ROOT}/src/Mothur.win.zip")

        return Mothur(mothur_path=f"{ROOT}/src/mothur/mothur.exe", verbosity=1)

    elif check_os() == "Linux":
        print("You are operating on Linux.")
        with open(f"{ROOT}/src/mothur_files/mothur_config.json", "r") as jsonfile:
            config = json.load(jsonfile)
        return Mothur(mothur_path=f'{config["linux_path"]}/mothur-1.46.1/mothur', verbosity=2)


def check_file(input_dir: str, file: str) -> bool:
    """
    Checks if file exists and if file is not empty. Returns True if file does exist or is empty.
    :return: True if file exists and is not empty
    """
    if os.path.isfile(f"{input_dir}/{file}"):
        print(f"File {file} exists", end=" ")
        if os.stat(f"{input_dir}/{file}").st_size != 0:
            print("and is not empty.")
            return True
        print("but is empty")
        os.remove(f"{input_dir}/{file}")
        return False
    else:
        print(f"{file} does not exist")
        return False


def run_mothur(input_dir: str, output_dir: str, rerun: bool = False, reclassify: bool = False) -> None:
    input_dir = os.path.join(ROOT, input_dir)
    output_dir = os.path.join(ROOT, output_dir)

    if not os.path.isdir(output_dir):
        os.makedirs(output_dir)

    with open(f"{ROOT}/src/mothur_files/mothur_config.json", "r") as jsonfile:
        config = json.load(jsonfile)
    prefix = config["file_prefix"]
    processors = config["processors"]

    m = get_mothur()
    m.set.logfile(name=config["logfile_name"], append="T")
    m.set.dir(input=input_dir)  # set folder where mothur is looking for input files

    if rerun:
        print("\nRerunning mothur, will create files even if already exists.")

    if not check_file(input_dir, f"{prefix}.files") or rerun:
        m.make.file(inputdir=input_dir, type=config["data_type"], prefix=prefix)

    if not check_file(input_dir, f"{prefix}.trim.contigs.fasta") or rerun:
        m.make.contigs(file=f"{prefix}.files", processors=processors, inputdir=input_dir)

    # Franzosa paper has the following filtering options:
    # (x) rejecting reads <200nt and >1000nt (minlegth=200,maxlength=1000)
    # (x) excluding homopolymer runs >6nt (maxhomop=6), accepting <=1.5 barcode correction (bdiff=2)
    # (x) 0 primer mismatches (pdiff = 0) and 0 ambiguous bases (maxambig = 0)
    # (x) a minimum average quality of 25 (qaverage=25)
    if not check_file(input_dir, f"{prefix}.trim.contigs.trim.fasta") or rerun:
        m.trim.seqs(fasta=f"{prefix}.trim.contigs.fasta", processors=processors, minlength=200, maxlength=1000,
                    maxhomop=6, bdiffs=2, pdiffs=0, maxambig=0, qaverage=25, inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.trim.unique.fasta") or rerun:
        m.unique.seqs(fasta=f"{prefix}.trim.contigs.trim.fasta", inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.trim.count_table") or rerun:
        m.count.seqs(name=f"{prefix}.trim.contigs.trim.names", group=f"{prefix}.contigs.groups",
                     inputdir=input_dir)

    tax_dir = f"{ROOT}/src/mothur_files"
    cutoff = config["cutoff"]
    # assign their sequences to the taxonomy outline of rdp6 file (version 6)
    if not check_file(input_dir, f"{prefix}.trim.contigs.trim.unique.trainset6_032010.wang.taxonomy") or (
            reclassify or rerun):
        m.classify.seqs(fasta=f"{prefix}.trim.contigs.trim.unique.fasta",
                        count=f"{prefix}.trim.contigs.trim.count_table",
                        template=f"{tax_dir}/trainset6_032010.fa",
                        taxonomy=f"{tax_dir}/trainset6_032010.tax",
                        output="simple", inputdir=input_dir, cutoff=cutoff,
                        processors=processors)

    # assign their sequences to the taxonomy outline of rdp6 file (version 18)
    if not check_file(input_dir, f"{prefix}.trim.contigs.trim.unique.rdp.wang.taxonomy") or (reclassify or rerun):
        m.classify.seqs(fasta=f"{prefix}.trim.contigs.trim.unique.fasta",
                        count=f"{prefix}.trim.contigs.trim.count_table",
                        template=f"{tax_dir}/trainset18_062020.rdp.fasta",
                        taxonomy=f"{tax_dir}/trainset18_062020.rdp.tax",
                        output="simple", inputdir=input_dir, cutoff=cutoff,
                        processors=processors)

    if check_file(input_dir, f"{prefix}.trim.contigs.trim.unique.trainset6_032010.wang.tax.summary"):
        m.rename.file(input=f"{prefix}.trim.contigs.trim.unique.trainset6_032010.wang.tax.summary",
                      new="final.rdp6.summary",
                      inputdir=input_dir, outputdir=output_dir)

    if check_file(input_dir, f"{prefix}.trim.contigs.trim.unique.rdp.wang.tax.summary"):
        m.rename.file(input=f"{prefix}.trim.contigs.trim.unique.rdp.wang.tax.summary", new="final.rdp18.summary",
                      inputdir=input_dir, outputdir=output_dir)

    print(f"Done processing with {cutoff} cutoff")


if __name__ == "__main__":
    ROOT = ".."
    run_mothur("data/vagina_momspi/visit1", "mothur_output/vagina_momspi/visit1")
