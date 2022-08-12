import typer
from src.create_files import *

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

if __name__ == "__main__":
    app()