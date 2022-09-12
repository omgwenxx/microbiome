import typer
from src.create_files import *
from src.download_files import *
from src.mothur_process import *
from src.util import *
from src.idability import *
from src.postprocessing import *

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
                    download_files(os.path.join(body_study_dir, file), os.path.join(".\data", destination))
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
            visit_dir = os.path.join(data_dir, body_study, visit)

            dir = os.listdir(visit_dir)
            if len(dir) == 0:
                print(f"{visit_dir} directory is empty.")
                continue

            output_dir = os.path.join("mothur_output", body_study, visit)
            run_mothur(visit_dir, output_dir)
            print("Creating taxonomy with mothur using files from:", visit)


def postprocess(data_dir: str = "mothur_output"):
    """
    Postprocesses all body site data folders.
    :return:
    """
    reformat_taxonomy(data_dir)
    unify_files()


@app.command()
def idability_code(data_dir: str, output_dir: str = "idability_output/codes") -> None:
    """
    Runs idability software to extract codes and confusion matrix
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(data_dir):
        if file.endswith("visit1.pcl"):
            print("Creating code for :", file)
            args_list = [os.path.join(data_dir, file), "-o", os.path.join(output_dir, file[:-4] + ".codes.txt")]
            run_idability(args_list)
            print()  # for improving readablity of output


@app.command()
def idability_eval(data_dir: str, code_dir: str = "idability_output/codes",
                   output_dir: str = "idability_output/eval") -> None:
    """
    Runs idability software to evaluate codes and print confusion matrix
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for file in os.listdir(data_dir):
        if file.endswith("visit2.pcl"):
            code_file = os.path.join(code_dir, file[:-5] + "1.codes.txt")
            print("Evaluating code for :", file)
            print("Using code file :", code_file)
            args_list = [os.path.join(data_dir, file),
                         "-c", os.path.join(code_dir, file[:-5] + "1.codes.txt"),
                         "-o", os.path.join(output_dir, file[:-4] + ".eval.txt")]
            run_idability(args_list)
            print()


if __name__ == "__main__":
    app() # uncomment to use cli interface

    # Run the app with completely new data
    # create files needed for download
    # create("hmp_portal_files/feces_ibdmdb_fastq") # do not have visit 1 and visit 2 samples
    # create("hmp_portal_files/feces_moms-pi_fastq")
    # create("hmp_portal_files/feces_t2d_fastq")
    # create("hmp_portal_files/vagina_moms-pi_fastq")

    # download files
    # download("download")

    # decompress files
    # extract("data")

    # remove compressed files
    # clean("data")

    # run mothur code
    extract_taxonomy("data")

    # format taxonomy files
    # postprocess()
    # idability_code("final_data/buccal_mucosa_momspi/rdp6")
    # idability_eval("final_data/buccal_mucosa_momspi/rdp6")
