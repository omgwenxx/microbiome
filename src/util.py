import os
import gzip
import shutil
"""
File containing utility functions for creating and modifing datasets
"""

def unpack_tar(body_folder: str) -> None:
    """
    Unpacks the downloaded files to the data folder
    """
    for visit in os.listdir(body_folder):
        for file in os.listdir(os.path.join(body_folder, visit)):
            current_file = os.path.join(body_folder, visit, file)
            destination = os.path.join(body_folder, visit)
            if file.endswith(".tar"):
                os.system(f"tar -xvf {current_file} -C {destination}")
                print("Unpacked file:", file)

def unpack_gz(body_folder:str) -> None:
    """
    Unpacks the downloaded files to the data folder
    """
    for visit in os.listdir(body_folder):
        for file in os.listdir(os.path.join(body_folder, visit)):
            current_file = os.path.join(body_folder, visit, file)

            if file.endswith(".gz"):
                print(current_file[:-3])
                with gzip.open(current_file, 'rb') as f_in:
                    with open(current_file[:-3], 'wb') as f_out:
                        print(f"fin: {f_in}")
                        print(f"fout: {f_out}")
                        shutil.copyfileobj(f_in, f_out)
                print("Unpacked file:", file)

if __name__ == "__main__":
    unpack_gz("../data/buccal_mucosa_momspi")