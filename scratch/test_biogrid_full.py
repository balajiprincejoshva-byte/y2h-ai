import requests
import zipfile
from pathlib import Path

headers = {'User-Agent': 'Mozilla/5.0'}
url = "https://downloads.thebiogrid.org/Download/BioGRID/Release-Archive/BIOGRID-4.4.240/BIOGRID-ORGANISM-4.4.240.tab3.zip"
out_zip = Path("data/raw/test_biogrid_organism.zip")
out_zip.parent.mkdir(parents=True, exist_ok=True)

print(f"Downloading full zip from {url}...")
r = requests.get(url, headers=headers, stream=True)
r.raise_for_status()

with open(out_zip, "wb") as f:
    for chunk in r.iter_content(chunk_size=65536):
        if chunk:
            f.write(chunk)

print(f"Full zip downloaded! Size: {out_zip.stat().st_size} bytes")

with zipfile.ZipFile(out_zip, 'r') as z:
    names = z.namelist()
    print(f"Zip archive contains {len(names)} files.")
    yeast_files = [n for n in names if 'Saccharomyces' in n]
    print(f"Yeast file inside zip: {yeast_files}")
