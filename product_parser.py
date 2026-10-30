"""Extract structured Product data from the JSON-LD embedded in HTML.

Returns a dictionary with name, SKU, price, currency, availability, brand
and identifiers where present, or None when no Product entity is found.
Missing fields mean unavailable metadata, not necessarily an absent product."""

import json
from bs4 import BeautifulSoup

# url = input("Enter product URL: ").strip()
# response = fetch_site(url)

# if response["status"] != "OK":
#     print("Cannot load product:", response["message"])
#     raise SystemExit

# STEP 1: Locate JSON-LD scripts in an already downloaded HTML document.
def extract_product(html):
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all (
        "script",
        attrs={"type" : "application/ld+json"}
    )

    # STEP 2: Decode blocks safely; a malformed block must not stop parsing.
    for script in scripts:
        try:
            data = json.loads(script.get_text())

        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]

        for item in items:
            if not isinstance(item, dict):
                continue

            # JSON-LD can place several linked entities inside @graph.
            entities = item.get("@graph", [item])

            if isinstance(entities, dict):
                entities = [entities]

            if not isinstance(entities, list):
                continue

            for entity in entities:
                if not isinstance(entity, dict):
                    continue

                types = entity.get("@type", [])

                if isinstance(types, str):
                    types = [types]

                # STEP 3: Ignore Organization, BreadcrumbList and other types.
                if "Product" not in types:
                    continue

                # product_found = True

                # STEP 4: Prices and availability belong to Product.offers.
                offers = entity.get("offers", {})

                # print("\nProduct name:", entity.get("name"))
                # print("SKU:", entity.get("sku"))

                if isinstance(offers, list):
                    offers = offers[0] if offers else {}

                if not isinstance(offers, dict):
                    offers = {}

                return {
                    "name": entity.get("name"),
                    "sku": entity.get("sku"),
                    "price": offers.get("price"),
                    "currency": offers.get("priceCurrency"),
                    "availability": offers.get("availability")
                }
            
    # No Product JSON-LD was found among the inspected entities.
    return None

    #             if isinstance(offers, list):
    #                 offers = offers[0] if offers else {}

    #             if isinstance(offers, dict):
    #                 print("Price:", offers.get("price"))
    #                 print("Currency:", offers.get("priceCurrency"))

    # if not product_found:
    #     print("No Product JSON-LD found")

    