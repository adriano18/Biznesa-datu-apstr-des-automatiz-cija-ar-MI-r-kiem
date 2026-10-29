import json
from bs4 import BeautifulSoup

# url = input("Enter product URL: ").strip()
# response = fetch_site(url)

# if response["status"] != "OK":
#     print("Cannot load product:", response["message"])
#     raise SystemExit

def extract_product(html):
    soup = BeautifulSoup(html, "html.parser")

    scripts = soup.find_all (
        "script",
        attrs={"type" : "application/ld+json"}
    )

    for script in scripts:
        try:
            data = json.loads(script.get_text())

        except json.JSONDecodeError:
            continue

        items = data if isinstance(data, list) else [data]

        for item in items:
            if not isinstance(item, dict):
                continue

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

                if "Product" not in types:
                    continue

                # product_found = True

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
            
    return None

    #             if isinstance(offers, list):
    #                 offers = offers[0] if offers else {}

    #             if isinstance(offers, dict):
    #                 print("Price:", offers.get("price"))
    #                 print("Currency:", offers.get("priceCurrency"))

    # if not product_found:
    #     print("No Product JSON-LD found")

    