# Note: GitPython requires git being installed on the system, and accessible via system's PATH.
from git import Repo
import os
import requests

ROOT = "."

def main():
    if not os.path.isfile(f"{ROOT}/src/idability.py"):
        print("Downloading idability...")
        url = "https://raw.githubusercontent.com/biobakery/idability/master/idability.py"
        r = requests.get(url)
        with open(f"{ROOT}/src/idability.py", 'wb') as f:
            f.write(r.content)
        print("Download complete.")



if __name__ == "__main__":
    ROOT=".."
    main()