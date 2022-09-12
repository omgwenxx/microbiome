from src.util import *
import os
import json
from mothur_py import Mothur
import requests

ROOT = "."
with open(f"{ROOT}/src/mothur_files/mothur_config.json", "r") as jsonfile:
    config = json.load(jsonfile)


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


def run_mothur(input_dir: str, output_dir: str, rerun: bool = False) -> None:
    input_dir = f"{ROOT}/{input_dir}"
    output_dir = f"{ROOT}/{output_dir}"

    prefix = config["file_prefix"]
    processors = config["processors"]

    m = get_mothur()
    m.set.logfile(name=config["logfile_name"], append="T")
    m.set.dir(input=input_dir)  # set folder where mothur is looking for input files

    if rerun:
        print("Rerunning mothur on already existing files.")

    if not check_file(input_dir, f"{prefix}.files") or rerun:
        m.make.file(inputdir=input_dir, type=config["data_type"], prefix=prefix)

    if not check_file(input_dir, f"{prefix}.trim.contigs.fasta") or rerun:
        m.make.contigs(file=f"{prefix}.files", processors=processors, inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.good.fasta") or rerun:
        m.screen.seqs(fasta=f"{prefix}.trim.contigs.fasta", contigsreport=f"{prefix}.contigs.report",
                      group=f"{prefix}.contigs.groups", maxambig=0, maxhomop=6, minlength=200, maxlength=1000,
                      mismatches=0,
                      processors=processors, inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.good.trim.fasta") or rerun:
        m.trim.seqs(fasta=f"{prefix}.trim.contigs.good.fasta", processors=processors, qaverage=25, inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.good.trim.unique.fasta") or rerun:
        m.unique.seqs(fasta=f"{prefix}.trim.contigs.good.trim.fasta", inputdir=input_dir)

    if not check_file(input_dir, f"{prefix}.trim.contigs.good.trim.count_table") or rerun:
        m.count.seqs(name=f"{prefix}.trim.contigs.good.trim.names", group=f"{prefix}.contigs.good.groups",
                     inputdir=input_dir)

    tax_dir = f"{ROOT}/src/mothur_files"
    # assign their sequences to the taxonomy outline of rdp file (version 6)
    if not check_file(input_dir, f"{prefix}.trim.contigs.good.trim.unique.trainset6_032010.wang.taxonomy") or rerun:
        m.classify.seqs(fasta=f"{prefix}.trim.contigs.good.trim.unique.fasta",
                        count=f"{prefix}.trim.contigs.good.trim.count_table",
                        template=f"{tax_dir}/trainset6_032010.fa",
                        taxonomy=f"{tax_dir}/trainset6_032010.tax",
                        output="simple", inputdir=input_dir,
                        processors=processors)

    # assign their sequences to the taxonomy outline of rdp file (version 18)
    if not check_file(input_dir, f"{prefix}.trim.contigs.good.trim.unique.rdp.wang.taxonomy") or rerun:
        m.classify.seqs(fasta=f"{prefix}.trim.contigs.good.trim.unique.fasta",
                        count=f"{prefix}.trim.contigs.good.trim.count_table",
                        template=f"{tax_dir}/trainset18_062020.rdp.fasta",
                        taxonomy=f"{tax_dir}/trainset18_062020.rdp.tax",
                        output="simple", inputdir=input_dir,
                        processors=processors)

    if check_file(input_dir, f"{prefix}.trim.contigs.good.trim.unique.trainset6_032010.wang.tax.summary"):
        m.rename.file(input=f"{prefix}.trim.contigs.good.trim.unique.trainset6_032010.wang.tax.summary",
                      new="final.rdp6.summary",
                      inputdir=input_dir, outputdir=output_dir)

    if check_file(input_dir, f"{prefix}.trim.contigs.good.trim.unique.rdp.wang.tax.summary"):
        m.rename.file(input=f"{prefix}.trim.contigs.good.trim.unique.rdp.wang.tax.summary", new="final.rdp18.summary",
                      inputdir=input_dir, outputdir=output_dir)


if __name__ == "__main__":
    ROOT = ".."
    run_mothur(input_dir=f"data/buccal_mucosa_momspi/visit1",
               output_dir="mothur_output/buccal_mucosa_momspi/visit1")
