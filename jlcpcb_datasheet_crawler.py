import os
import json
import time
import requests
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options

# Set up paths
BOM_FILE = "bom.xls"
LINKS_FILE = "links.json"
DATASHEETS_FILE = "datasheets.json"
DATASHEET_FOLDER = "datasheets"
GECKODRIVER_PATH = "/usr/local/bin/geckodriver"

# Ensure datasheet folder exists
os.makedirs(DATASHEET_FOLDER, exist_ok=True)

# Configure headless Firefox
options = Options()
options.headless = True
service = Service(GECKODRIVER_PATH)
driver = webdriver.Firefox(service=service, options=options)

# Headers to mimic a real browser
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Referer": "https://jlcpcb.com/",
}

# Step 1: Extract part URLs from JLCPCB search
print("Extracting part URLs...")
df = pd.read_excel(BOM_FILE)

# Check for the required column
part_column = None
if "JLCPCB Part #" in df.columns:
    part_column = "JLCPCB Part #"
elif "Supplier Part" in df.columns:
    part_column = "Supplier Part"
else:
    raise ValueError("Neither 'JLCPCB Part #' nor 'Supplier Part' column found in BOM file")

part_numbers = df[part_column].dropna().tolist()
part_links = {}
for part_number in part_numbers:
    search_url = f"https://jlcpcb.com/parts/componentSearch?searchTxt={part_number}"
    driver.get(search_url)
    driver.implicitly_wait(10)
    links = driver.find_elements(By.TAG_NAME, "a")
    for link in links:
        href = link.get_attribute("href")
        if href and "jlcpcb.com/partdetail/" in href:
            part_links[part_number] = href
            break

with open(LINKS_FILE, "w") as file:
    json.dump(part_links, file, indent=4)
print(f"Saved {len(part_links)} part URLs to {LINKS_FILE}")

# Step 2: Extract datasheet URLs
print("Extracting datasheet URLs...")
datasheets = []
for part_number, part_url in part_links.items():
    driver.get(part_url)
    driver.implicitly_wait(10)
    try:
        datasheet_element = driver.find_element(By.XPATH, "//dt[text()='Datasheet']/following-sibling::dd/a")
        datasheet_url = datasheet_element.get_attribute("href")
        datasheets.append({"part_number": part_number, "datasheet_url": datasheet_url})
        print(f"✅ Found datasheet for {part_number}: {datasheet_url}")
    except Exception as e:
        print(f"⚠️ No datasheet found for {part_number}")

with open(DATASHEETS_FILE, "w") as file:
    json.dump(datasheets, file, indent=4)
print(f"Saved datasheet URLs to {DATASHEETS_FILE}")

# Step 3: Download datasheets
def download_pdf(url, filename):
    try:
        response = requests.get(url, headers=HEADERS, stream=True)
        response.raise_for_status()
        filepath = os.path.join(DATASHEET_FOLDER, filename)
        with open(filepath, "wb") as pdf_file:
            for chunk in response.iter_content(chunk_size=8192):
                pdf_file.write(chunk)
        print(f"✅ Downloaded: {filename}")
    except requests.RequestException as e:
        print(f"❌ Failed to download {url}: {e}")

print("Downloading datasheets...")
for entry in datasheets:
    datasheet_url = entry.get("datasheet_url")
    if datasheet_url:
        filename = f"{entry['part_number']}.pdf"
        download_pdf(datasheet_url, filename)
    else:
        print(f"⚠️ No datasheet URL found for {entry['part_number']}")

driver.quit()
print("🎉 All datasheets processed and downloaded!")
