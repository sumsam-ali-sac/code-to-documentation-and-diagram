import urllib.request
import zipfile
import os
import shutil

url = "https://github.com/mingrammer/diagrams/archive/refs/heads/master.zip"
zip_path = "diagrams.zip"

print("Downloading diagrams repository zip (this may take a minute)...")
urllib.request.urlretrieve(url, zip_path)

print("Extracting zip file...")
with zipfile.ZipFile(zip_path, 'r') as zip_ref:
    zip_ref.extractall("temp_diagrams")

print("Moving resources to autodoc/assets/icons...")
os.makedirs("autodoc/assets", exist_ok=True)
if os.path.exists("autodoc/assets/icons"):
    shutil.rmtree("autodoc/assets/icons")

shutil.move("temp_diagrams/diagrams-master/resources", "autodoc/assets/icons")

print("Cleaning up...")
shutil.rmtree("temp_diagrams")
os.remove(zip_path)

print("Successfully downloaded and extracted icons!")
