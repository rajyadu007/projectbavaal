import requests
import xml.etree.ElementTree as ET

# Your existing import function
from tools.import_webstory import import_webstory_from_url  # adjust the path to where your function is

SITEMAP_URL = "https://bavaal.com/web-story-sitemap.xml"

def import_all_webstories_from_sitemap():
    print(f"Fetching sitemap: {SITEMAP_URL}")
    response = requests.get(SITEMAP_URL)
    response.raise_for_status()

    # Parse XML
    root = ET.fromstring(response.content)
    namespaces = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}

    urls = [loc.text for loc in root.findall(".//ns:loc", namespaces)]
    print(f"Found {len(urls)} web stories")

    for url in urls:
        print(f"Importing: {url}")
        try:
            import_webstory_from_url(url)
        except Exception as e:
            print(f"❌ Failed to import {url}: {e}")

# Run it
if __name__ == "__main__":
    import_all_webstories_from_sitemap()
