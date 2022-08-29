from src.util import *
import os
import json
from mothur_py import Mothur
import requests

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
        # TODO add Linux support
        # m = Mothur(mothur_path='<path>/mothur-1.46.1/mothur', verbosity=2)
        return None


def run_mothur(input_dir: str, output_dir: str):
    with open(f"{ROOT}/src/mothur_files/mothur_config.json", "r") as jsonfile:
        config = json.load(jsonfile)

    input_dir = f"{ROOT}/{input_dir}"
    output_dir = f"{ROOT}/{output_dir}"

    PREFIX = config["file_prefix"]

    m = get_mothur()
    # m.set.logfile(name=config["logfile_name"], append="T")

    m.set.logfile(name="silent")
    # TODO flexible input folder
    m.set.dir(input=input_dir)  # set folder where mothur is looking for input files
    m.make.file(inputdir=input_dir, type=config["data_type"], prefix=PREFIX)
    m.make.contigs(file=f"{PREFIX}.files", processors=8, inputdir=input_dir)
    m.screen.seqs(fasta="stability.trim.contigs.fasta", contigsreport="stability.contigs.report",
                  group="stability.contigs.groups", maxambig=0, maxhomop=6, minlength=200, maxlength=1000, mismatches=0,
                  processors=56, inputdir=input_dir)

    m.trim.seqs(fasta="stability.trim.contigs.good.fasta", processors=56, qaverage=25, inputdir=input_dir)
    m.unique.seqs(fasta="stability.trim.contigs.good.trim.fasta", inputdir=input_dir)

    m.count.seqs(name="stability.trim.contigs.good.trim.names", group="stability.contigs.good.groups",
                 inputdir=input_dir)

    TAX_DIR = f"{ROOT}/src/mothur_files"
    # assign their sequences to the taxonomy outline of rdp file (version 6)
    m.classify.seqs(fasta="stability.trim.contigs.good.trim.unique.fasta",
                    count="stability.trim.contigs.good.trim.count_table",
                    template=f"{TAX_DIR}/trainset6_032010.fa",
                    taxonomy=f"{TAX_DIR}/trainset6_032010.tax",
                    output="simple", inputdir=input_dir,
                    processors=56)

    # assign their sequences to the taxonomy outline of rdp file (version 18)
    m.classify.seqs(fasta="stability.trim.contigs.good.trim.unique.fasta",
                    count="stability.trim.contigs.good.trim.count_table",
                    template=f"{TAX_DIR}/trainset18_062020.rdp.fasta",
                    taxonomy=f"{TAX_DIR}/trainset18_062020.rdp.tax",
                    output="simple", inputdir=input_dir,
                    processors=56)

    m.rename.file(input="stability.trim.contigs.good.trim.unique.trainset6_032010.wang.tax.summary",
                  new="final.rdp6.summary",
                  inputdir=input_dir, outputdir=output_dir)
    m.rename.file(input="stability.trim.contigs.good.trim.unique.rdp.wang.tax.summary", new="final.rdp18.summary",
                  inputdir=input_dir, outputdir=output_dir)


if __name__ == "__main__":
    ROOT = ".."
    run_mothur(input_dir="data/buccal_mucosa_momspi/visit1",
               output_dir="mothur_output/buccal_mucosa_momspi/visit1")
