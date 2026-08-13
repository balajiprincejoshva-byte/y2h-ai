import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
headers = {'User-Agent': 'Mozilla/5.0'}

urls = [
    "https://mips.helmholtz-muenchen.de/proj/ppi/negatome/combined_stringent.txt",
    "https://mips.helmholtz-muenchen.de/proj/ppi/negatome/manual_stringent.txt"
]

for url in urls:
    try:
        r = requests.get(url, headers=headers, verify=False, timeout=15)
        print(f"URL: {url} | Status: {r.status_code} | Size: {len(r.text)} bytes")
        if r.status_code == 200:
            lines = r.text.splitlines()
            print("First 3 lines:", lines[:3])
            # Check how many yeast entries are present
            yeast_lines = [l for l in lines if 'Y' in l or 'YEAST' in l or 'P' in l]
            print(f"Sample entries count: {len(lines)}")
            break
    except Exception as e:
        print(f"Error for {url}: {e}")
