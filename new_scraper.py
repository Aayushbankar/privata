import os
import asyncio
from urllib.parse import urlparse
from crawl4ai import AsyncWebCrawler

BASE_DIR = "crw4ai_output"
os.makedirs(BASE_DIR, exist_ok=True)

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

async def crawl_all():
    async with AsyncWebCrawler() as crawler:
        for url in URLS:
            parsed = urlparse(url)
            path = parsed.path.strip("/")
            filename = "home" if not path else path.replace("/", "_")
            domain_dir = os.path.join(BASE_DIR, parsed.netloc)
            os.makedirs(domain_dir, exist_ok=True)
            out_file = os.path.join(domain_dir, f"crw4ai_{filename}.md")

            print(f"[INFO] Crawling {url} -> {out_file}")
            result = await crawler.arun(url=url)

            with open(out_file, "w", encoding="utf-8") as f:
                f.write(result.markdown or "")

if __name__ == "__main__":
    asyncio.run(crawl_all())
