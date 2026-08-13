import requests
import zipfile
import io

headers = {'User-Agent': 'Mozilla/5.0'}

url = "https://downloads.thebiogrid.org/Download/BioGRID/Latest-Release/BIOGRID-ORGANISM-LATEST.tab3.zip"
print(f"Downloading {url}...")
r = requests.get(url, headers=headers, stream=True)
print("Status:", r.status_code)

content = bytearray()
for chunk in r.iter_content(chunk_size=65536):
    if chunk:
        content.extend(chunk)
        if len(content) % (1024*1024) < 65536:
            print(f"Downloaded {len(content)//(1024*1024)} MB...")

print(f"Total downloaded test bytes: {len(content)}")
with zipfile.ZipFile(io.BytesIO(content), 'r') as z:
    names = z.namelist()
    print("Sample zip contents:", names[:10])
    yeast_files = [n for n in names if 'Saccharomyces' in n]
    print("Yeast files found inside zip:", yeast_files)
