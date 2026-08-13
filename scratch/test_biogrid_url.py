import requests
import re

headers = {'User-Agent': 'Mozilla/5.0'}

# Test BioGRID-ORGANISM-LATEST.tab3.zip
url_organism = "https://downloads.thebiogrid.org/File/BioGRID/Latest-Release/BIOGRID-ORGANISM-LATEST.tab3.zip"
r = requests.head(url_organism, headers=headers)
print(f"BIOGRID-ORGANISM-LATEST.tab3.zip HEAD Status: {r.status_code}, Content-Length: {r.headers.get('Content-Length')}")

# Find recent versions on release archive
r_arch = requests.get("https://downloads.thebiogrid.org/BioGRID/Release-Archive/", headers=headers)
versions = sorted(list(set(re.findall(r'BIOGRID-(\d+\.\d+\.\d+)', r_arch.text))), key=lambda x: [int(p) for p in x.split('.')])
print(f"Latest 5 archived versions: {versions[-5:]}")

# Test downloading yeast file for latest available version in archive
for ver in reversed(versions[-5:]):
    file_name = f"BIOGRID-ORGANISM-Saccharomyces_cerevisiae_S288c-{ver}.tab3.zip"
    url_test = f"https://downloads.thebiogrid.org/File/BioGRID/Release-Archive/BIOGRID-{ver}/{file_name}"
    r_test = requests.head(url_test, headers=headers)
    print(f"Testing version {ver}: status={r_test.status_code}, url={url_test}")
    if r_test.status_code == 200:
        print(f"FOUND VALID RELEASE: {ver} -> {url_test}")
        break
