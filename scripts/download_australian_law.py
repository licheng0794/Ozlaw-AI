import os
import requests

# List of (act name, AustLII text file URL) pairs
ACTS = [
    ("Criminal_Code_Act_1995", "https://www.austlii.edu.au/cgi-bin/download.cgi/cgi-bin/download.cgi/download/au/legis/cth/consol_act/cca1995115.txt"),
    ("Competition_and_Consumer_Act_2010", "https://www.austlii.edu.au/cgi-bin/download.cgi/cgi-bin/download.cgi/download/au/legis/cth/consol_act/caca2010265.txt"),
]

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../data/'))
os.makedirs(DATA_DIR, exist_ok=True)

def download_text_file(name, url):
    print(f"Downloading {name} from {url}")
    try:
        resp = requests.get(url)
        resp.raise_for_status()
        
        # Save as text file
        file_path = os.path.join(DATA_DIR, f"{name}.txt")
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(resp.text)
        
        print(f"Saved to {file_path}")
        print(f"Content length: {len(resp.text)} characters")
        
    except Exception as e:
        print(f"Error downloading {name}: {e}")

if __name__ == "__main__":
    for name, url in ACTS:
        download_text_file(name, url) 