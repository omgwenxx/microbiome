import typer
from src.create_files import *
from src.download_files import *

app = typer.Typer()

@app.command()
def create(input_dir: str = typer.Argument(..., help='Folder with files containing download and metadata information'),
           num_visits: int = typer.Argument(2, help='Number of visits to download')) -> None:
    """
    Creates folder with files per body site and visit for downloading and metadata.
    :param num_visits:
    :param input_dir: Folder with files containing download and metadata information
    :return:
    """
    merge_files(input_dir)
    create_folders()
    export_all(num_visits)
    print("Done creating folders and files for download.")

@app.command()
def download(download_dir: str = typer.Argument(..., help='Folder with files containing download information')) -> None:
    """
    Downloads files from the portal.
    :param download_dir: Folder with files containing download information
    :return:
    """
    first_folder = True # for formatting console output

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
                    download_files(os.path.join(body_study_dir, file), os.path.join(".\data",destination))
                    print("Downloaded file:", file)

    print("\nDone downloading files.")

if __name__ == "__main__":
    # app() # uncomment to use cli interface
    download("download")