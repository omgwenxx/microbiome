from util import *
import os
import shutil
import requests

m = None

if check_os() == "Windows":
    print("You are operating on Windows.")

    # check if folder exists
    if not os.path.isfile("./Mothur.win.zip"):
        print("Downloading Mothur...")
        url = "https://github.com/mothur/mothur/releases/download/v1.48.0/Mothur.win.zip"
        r = requests.get(url)
        with open("Mothur.win.zip", 'wb') as f:
            f.write(r.content)
        print("Download complete.")

unpack_zip("Mothur.win.zip")
