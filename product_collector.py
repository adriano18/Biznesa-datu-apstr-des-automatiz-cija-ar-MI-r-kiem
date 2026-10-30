"""Download a bounded sample of candidate URLs and extract Product JSON-LD.

The input URLs come from sitemap_reader. The output is a list of product
records with source URLs; category pages and inaccessible pages are skipped.
This is a sample, not an estimate of the entire shop assortment."""

from time import sleep
from fetch_sites import fetch_site
from product_parser import extract_product

# STEP 1: Try candidate pages until the requested number of products is found.
def collect_products(urls, limit=3):
    products = []

    for url in urls:
        if len(products) >= limit:
            break

        print("\nAnalyzing:", url)

        # STEP 2: Reuse the HTTP loader and its robots.txt check.
        response = fetch_site(url)

        if response["status"] == "OK":
            # STEP 3: A valid Product entity distinguishes products from categories.
            product = extract_product(response["html"])

            if product:
                product["url"] = url
                products.append(product)

                print("Name:", product["name"])
                print("Price:", product["price"])
                print("Availability:", product["availability"])

            else:
                print("Product JSON-LD not found")
        else:
            print("Fetch status:", response["status"])

        # STEP 4: Pause between requests to reduce load on shop servers.
        sleep(1)

    # A list of dictionaries is easy to convert to a Pandas DataFrame.
    return products