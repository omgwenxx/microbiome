import typer
from src.create_files import *
from src.download_files import *
from src.mothur_process import *
from src.util import *
from src.idability import *
from src.postprocessing import *
from typing import Optional

app = typer.Typer()


@app.command()
def create(input_dir: str = typer.Argument(..., help='Folder with files containing download and metadata information'),
           num_visits: int = 2) -> None:
    """
    Creates two folders with files per body site and visit, one downloading and metadata.
    :param num_visits:
    :param input_dir: Folder with files containing download and metadata information
    :return:
    """
    merge_files(input_dir)
    create_folders()
    print(f"\nCreating files for {num_visits} visits")
    export_all(num_visits)
    print("Done creating folders and files for download.")


@app.command()
def download(download_dir: str = typer.Argument(..., help='Folder with files containing download information')) -> None:
    """
    Downloads files from the portal.
    :param download_dir: Folder with files containing download information
    :return:
    """
    first_folder = True  # for formatting console output

    # get all possible folders with files
    for folder in os.listdir(download_dir):
        if os.path.isdir(os.path.join(download_dir, folder)):
            body_study_dir = os.path.join(download_dir, folder)

            if first_folder:
                print(f"Download files from {body_study_dir}")
                first_folder = False
            else:
                print(f"\nDownload files from {body_study_dir}")

            for file in os.listdir(body_study_dir):
                if file.endswith(".tsv"):
                    destination = os.path.join(folder, file[:-4])
                    download_files(os.path.join(body_study_dir, file), os.path.join("./data", destination))
                    print("Downloaded file:", file)

    print("\nDone downloading files.")


@app.command()
def decompress(data_dir: str = typer.Argument(..., help='Folder with downloaded files')) -> None:
    """
    Unzips all downloaded files.
    :param data_dir: Folder with downloaded files
    :return:
    """
    for folder in os.listdir(data_dir):
        print("Extracting files from:", folder)
        body_study_dir = os.path.join(data_dir, folder)
        unpack_tar(body_study_dir)
        unpack_gz(body_study_dir)

    print("\nDone extracting files.")


@app.command()
def clean(data_dir: str = typer.Argument(..., help='Folder with downloaded files')) -> None:
    """
    Cleans all body site data folders of .tar and .gz files.
    :return:
    """
    for folder in os.listdir(data_dir):
        print("Cleaning files from:", folder)
        body_study_dir = os.path.join(data_dir, folder)
        clean_folder(body_study_dir)

    print("\nDone cleaning folders.")


@app.command()
def extract_taxonomy(data_dir: str):
    if not os.path.exists("mothur_output"):
        os.mkdir("mothur_output")

    for body_study in os.listdir(data_dir):
        for visit in os.listdir(os.path.join(data_dir, body_study)):
            print("Creating taxonomy with mothur using files from:", visit)
            visit_dir = os.path.join(data_dir, body_study, visit)

            dir = os.listdir(visit_dir)
            if len(dir) == 0:
                print(f"{visit_dir} directory is empty.")
                continue

            output_dir = os.path.join("mothur_output", body_study, visit)
            run_mothur(visit_dir, output_dir)

    print("Done creating mothur files.")


@app.command()
def postprocess(data_dir: Optional[str] = typer.Argument("mothur_output", help='Folder with output files from mothur process')):
    """
    Postprocesses all body site data folders.
    :return:
    """
    reformat_taxonomy(data_dir)
    unify_files()


@app.command()
def idability(data_dir: str, code_visit: str = "visit1") -> None:
    """
    Runs idability software to extract codes and confusion matrix
    """
    code_dir = "idability_output/codes"
    if not os.path.exists(code_dir):
        os.makedirs(code_dir)

    code_file = ""
    for file in os.listdir(data_dir):
        if file.endswith(f"{code_visit}.pcl"):
            print("Creating code for :", file)
            code_file = os.path.join(code_dir, file[:-4] + ".codes.txt")
            args_list = [os.path.join(data_dir, file), "-o", code_file]
            run_idability(args_list)
            print()  # for improving readablity of output

    eval_dir: str = "idability_output/eval"

    if not os.path.exists(eval_dir):
        os.makedirs(eval_dir)

    for file in os.listdir(data_dir):
        if not file.endswith("visit2.pcl"):
            print("Evaluating code for :", file)
            print("Using code file :", code_file)
            args_list = [os.path.join(data_dir, file),
                         "-c", code_file,
                         "-o", os.path.join(eval_dir, file[:-4] + ".eval.txt")]
            run_idability(args_list)
            print()

if __name__ == "__main__":
    app() # uncomment to use cli interface

    # Run the app with completely new data
    # create files needed for download
    # create("hmp_portal_files/feces_ibdmdb_fastq") # do not have visit 1 and visit 2 samples
    # create("hmp_portal_files/feces_momspi_fastq")
    # create("hmp_portal_files/feces_t2d_fastq")
    # create("hmp_portal_files/vagina_momspi_fastq")

    # download files
    # download("download")

    # decompress files
    # decompress("data")

    # remove compressed files
    # clean("data")

    # run mothur code
    # extract_taxonomy("data")

    # format taxonomy files
    # postprocess("ifs_mothur_output")
    # idability("final_data/vagina_momspi/rdp18")