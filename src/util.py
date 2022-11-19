import gzip
import os
import shutil
import zipfile

"""
File containing utility functions for creating and modifing datasets
"""


def unpack_tar(body_folder: str) -> None:
    """
    Unpacks .tar files to the folder
    :param body_folder: Folder with .tar files
    """
    for visit in os.listdir(body_folder):
        for file in os.listdir(os.path.join(body_folder, visit)):
            current_file = os.path.join(body_folder, visit, file)
            destination = os.path.join(body_folder, visit)
            if file.endswith(".tar"):
                os.system(f"tar -xvf {current_file} -C {destination}")
                print("Unpacked file:", file)


def unpack_gz(body_folder: str) -> None:
    """
    Unpacks .gz files to the folder
    :param body_folder: Folder with .gz files
    """
    for visit in os.listdir(body_folder):
        for file in os.listdir(os.path.join(body_folder, visit)):
            current_file = os.path.join(body_folder, visit, file)

            if file.endswith(".gz"):
                with gzip.open(current_file, 'rb') as f_in:
                    with open(current_file[:-3], 'wb') as f_out:
                        print(f"fin: {f_in}")
                        print(f"fout: {f_out}")
                        shutil.copyfileobj(f_in, f_out)
                print("Unpacked file:", file)


def unpack_zip(file_path: str) -> None:
    """
    Unpacks a zip file
    """
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        zip_ref.extractall(f"./src/")
    print("Unpacked file:", file_path)


def clean_folder(body_folder: str) -> None:
    """
    Removes all files in the data folder
    """
    count = 0
    for visit in os.listdir(body_folder):
        for file in os.listdir(os.path.join(body_folder, visit)):
            current_file = os.path.join(body_folder, visit, file)

            if current_file.endswith(".gz") or current_file.endswith(".tar"):
                os.remove(current_file)
                count = count + 1

    print(f"Removed .tar and .gz files from {body_folder}, total of {count} files.")


def check_os():
    """
    Checks if the operating system is Windows or Linux
    """
    if os.name == 'nt':
        return "Windows"
    else:
        return "Linux"


if __name__ == "__main__":
    print(check_os())
