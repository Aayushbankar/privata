import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# Base URL
BASE_URL = "https://mosdac.gov.in/"

# Sitemap links you provided
URLS = [
    "https://mosdac.gov.in/",
    "https://mosdac.gov.in/insat-3dr",
    "https://mosdac.gov.in/insat-3d",
    "https://mosdac.gov.in/kalpana-1",
    "https://mosdac.gov.in/insat-3a",
    "https://mosdac.gov.in/megha-tropiques",
    "https://mosdac.gov.in/saral-altika",
    "https://mosdac.gov.in/oceansat-2",
    "https://mosdac.gov.in/oceansat-3",
    "https://mosdac.gov.in/insat-3ds",
    "https://mosdac.gov.in/scatsat-1",
    "https://mosdac.gov.in/internal/catalog-satellite",
    "https://mosdac.gov.in/internal/catalog-insitu",
    "https://mosdac.gov.in/internal/catalog-radar",
    "https://mosdac.gov.in/internal/gallery",
    "https://mosdac.gov.in/internal/gallery/weather",
    "https://mosdac.gov.in/internal/gallery/ocean",
    "https://mosdac.gov.in/internal/gallery/dwr",
    "https://mosdac.gov.in/internal/gallery/current",
    "https://mosdac.gov.in/internal/uops",
    "https://mosdac.gov.in/user-manual-mosdac-data-download-api",
    "https://mosdac.gov.in/bayesian-based-mt-saphir-rainfall",
    "https://mosdac.gov.in/gps-derived-integrated-water-vapour",
    "https://mosdac.gov.in/gsmap-isro-rain",
    "https://mosdac.gov.in/meteosat8-cloud-properties",
    "https://mosdac.gov.in/3d-volumetric-terls-dwrproduct",
    "https://mosdac.gov.in/inland-water-height",
    "https://mosdac.gov.in/river-discharge",
    "https://mosdac.gov.in/soil-moisture-0",
    "https://mosdac.gov.in/global-ocean-surface-current",
    "https://mosdac.gov.in/high-resolution-sea-surface-salinity",
    "https://mosdac.gov.in/indian-mainland-coastal-product",
    "https://mosdac.gov.in/ocean-subsurface",
    "https://mosdac.gov.in/oceanic-eddies-detection",
    "https://mosdac.gov.in/sea-ice-occurrence-probability",
    "https://mosdac.gov.in/wave-based-renewable-energy",
    "https://mosdac.gov.in/internal/calval-data",
    "https://mosdac.gov.in/internal/forecast-menu",
    "https://mosdac.gov.in/rss-feed",
    "https://mosdac.gov.in/insitu",
    "https://mosdac.gov.in/calibration-reports",
    "https://mosdac.gov.in/validation-reports",
    "https://mosdac.gov.in/data-quality",
    "https://mosdac.gov.in/weather-reports",
    "https://mosdac.gov.in/atlases",
    "https://mosdac.gov.in/tools",
    "https://mosdac.gov.in/sitemap",
    "https://mosdac.gov.in/help",
    "https://mosdac.gov.in/mosdac-feedback",
    "https://mosdac.gov.in/about-us",
    "https://mosdac.gov.in/contact-us",
    "https://mosdac.gov.in/copyright-policy",
    "https://mosdac.gov.in/data-access-policy",
    "https://mosdac.gov.in/hyperlink-policy",
    "https://mosdac.gov.in/privacy-policy",
    "https://mosdac.gov.in/website-policies",
    "https://mosdac.gov.in/terms-conditions",
    "https://mosdac.gov.in/faq-page",
    "https://mosdac.gov.in/internal/registration",
    "https://mosdac.gov.in/internal/uops",
    "https://mosdac.gov.in/internal/logout",
]

# Folder to store scraped text files
OUTPUT_DIR = "mosdac_scraped"
os.makedirs(OUTPUT_DIR, exist_ok=True)


def clean_filename(url: str) -> str:
    """Generate safe filename from URL path."""
    parsed = urlparse(url)
    path = parsed.path.strip("/").replace("/", "_")
    if not path:
        path = "home"
    return path + ".txt"


def scrape_and_save(url: str):
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"[ERROR] Cannot fetch {url}: {e}")
        return

    soup = BeautifulSoup(response.text, "html.parser")

    # Extract text from page
    texts = []
    for element in soup.find_all(["h1", "h2", "h3", "h4", "h5", "p", "li", "td", "span"]):
        content = element.get_text(strip=True)
        if content:
            texts.append(content)

    content_text = "\n".join(texts)

    # Save to file
    filename = clean_filename(url)
    filepath = os.path.join(OUTPUT_DIR, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(f"URL: {url}\n\n")
        f.write(content_text)

    print(f"[SAVED] {url} -> {filename}")


if __name__ == "__main__":
    for link in URLS:
        scrape_and_save(link)
