"""Optional live smoke test of IKEA's Latvian product XML sitemap.

Reads the global index, selects prod-lv-LV_*.xml and tests one product URL.
This is a network test, not an offline unit test, and needs site access."""

import requests
import xml.etree.ElementTree as ET
from fetch_sites import fetch_site
from product_parser import extract_product

# STEP 1: Read IKEA's global sitemap index as an optional compatibility test.
url = "https://www.ikea.com/sitemaps/sitemap.xml"

response = requests.get(url, timeout=(10, 30))
response.raise_for_status()

root = ET.fromstring(response.content)

sitemaps = [
    link.text.strip()
    for link in root.findall(".//{*}sitemap/{*}loc")
    if link.text
]

# STEP 2: Select the six Latvian-market product sitemap files.
latvian_sitemaps = [
    link for link in sitemaps
    if "/prod-lv-LV_" in link
]

print("Total sitemap files:", len(sitemaps))
print("Latvian product sitemaps:", len(latvian_sitemaps))

print("\nFirst 3 Latvian sitemaps:")

for link in latvian_sitemaps[:3]:
    print(link)


# STEP 3: Read only the first product sitemap; do not scrape the whole catalog.
if latvian_sitemaps:
    product_sitemap_url = latvian_sitemaps[0]

    print("\nReading:", product_sitemap_url)

    product_response = requests.get(
        product_sitemap_url,
        timeout=(10, 30)
    )

    product_response.raise_for_status()

    product_root = ET.fromstring(product_response.content)

    if product_root.tag.endswith("urlset"):
        product_links = product_root.findall(
            ".//{*}url/{*}loc"
        )

        print("Product URLs:", len(product_links))

        print("\nFirst 5 product URLs:")

        for link in product_links[:5]:
            print(link.text)

        
        if product_links:
            product_url = product_links[0].text.strip()

            print("\nTesting IKEA product:", product_url)

            product_data = fetch_site(product_url)

            print("Fetch status:", product_data["status"])

            if product_data["status"] == "OK":
                product = extract_product(product_data["html"])

                if product:
                    print("\nProduct found!")
                    print("Name:", product["name"])
                    print("SKU:", product["sku"])
                    print("Price:", product["price"])
                    print("Currency:", product["currency"])
                    print("Availability:", product["availability"])
                else:
                    print("Product JSON-LD not found")
            else:
                print("Reason:", product_data["message"])

    else:
        print("Unexpected XML structure:", product_root.tag)

