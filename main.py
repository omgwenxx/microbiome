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
    Creates folder with files per body site and visit for downloading and metadata.
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
def extract(data_dir: str = typer.Argument(..., help='Folder with downloaded files')) -> None:
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


@app.command()
def extract_taxonomy(data_dir: str):
    if not os.path.exists("mothur_output"):
        os.mkdir("mothur_output")

    for folder in os.listdir(data_dir):
        for visit in os.listdir(os.path.join(data_dir, folder)):
            visit_dir = os.path.join(data_dir, folder, visit)

            dir = os.listdir(visit_dir)
            if len(dir) == 0:
                print(f"{visit_dir} directory is empty.")
                continue

            output_dir = os.path.join("mothur_output", folder, visit)
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
def idability_code() -> None:
    """
    Runs idability software to extract codes and confusion matrix
    """
    # DATA_DIR = "final_data/buccal_mucosa_momspi/rdp6"
    DATA_DIR = "idability_data/otus-tables"
    OUTPUT_DIR = "idability_output/codes"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for file in os.listdir(DATA_DIR):
        if file.endswith("visit1.pcl"):
            print("Creating code for :", file)
            args_list = [os.path.join(DATA_DIR, file), "-o", os.path.join(OUTPUT_DIR, file[:-4] + ".codes.txt")]
            run_idability(args_list)
            print()  # for improving readablity of output


@app.command()
def idability_eval() -> None:
    """
    Runs idability software to evaluate codes and print confusion matrix
    """
    # DATA_DIR = "final_data/buccal_mucosa_momspi/rdp6"
    DATA_DIR = "idability_data/otus-tables"
    CODE_DIR = "idability_output/codes"
    OUTPUT_DIR = "idability_output/eval"

    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    for file in os.listdir(DATA_DIR):
        if file.endswith("visit2.pcl"):
            code_file = os.path.join(CODE_DIR, file[:-5] + "1.codes.txt")
            print("Evaluating code for :", file)
            print("Using code file :", code_file)
            args_list = [os.path.join(DATA_DIR, file),
                         "-c", os.path.join(CODE_DIR, file[:-5] + "1.codes.txt"),
                         "-o", os.path.join(OUTPUT_DIR, file[:-4] + ".eval.txt")]
            run_idability(args_list)
            print()


if __name__ == "__main__":
    # app() # uncomment to use cli interface
    # create("example_input")
    # download("download")
    # extract("data")
    # clean("data")
    # extract_taxonomy("data")
    postprocess()
    # idability_code()
    # idability_eval()
