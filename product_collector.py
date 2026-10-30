from time import sleep
from fetch_sites import fetch_site
from product_parser import extract_product

def collect_products(urls, limit=3):
    products = []

    for url in urls:
        if len(products) >= limit:
            break

        print("\nAnalyzing:", url)

        response = fetch_site(url)

        if response["status"] == "OK":
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

        sleep(1)

    return products