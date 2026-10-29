import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse
from fetch_sites import fetch_site
from bs4 import BeautifulSoup
from product_parser import extract_product
from time import sleep
import pandas as pd
from pathlib import Path

site = input("Enter shop URL: ").strip()
parsed_site = urlparse(site)
base_url = f"{parsed_site.scheme}://{parsed_site.netloc}"

headers = {
        "User-Agent" : "EcommerceAuditAnalyzerBot/0.1"
    }

try:
    robots_response = requests.get(
        base_url + "/robots.txt",
        headers=headers,
        timeout=15
    )

except requests.RequestException as error:
    print("Cannot check robots.txt:", error)
    raise SystemExit

sitemap_urls = []

if robots_response.status_code == 200:
    for line in robots_response.text.splitlines():
        if line.lower().startswith("sitemap:"):
            sitemap_urls.append(line.split(":", 1)[1].strip())

elif robots_response.status_code != 404:
    print("Cannot verify robots.txt. Stopping.")
    raise SystemExit

if not sitemap_urls:
    sitemap_urls = [
        base_url + "/sitemap.xml",
        base_url + "/sitemap-index.xml",
        base_url + "/wp-sitemap.xml"
    ]

for sitemap_url in sitemap_urls[:5]:
    print("\nChecking:", sitemap_url)

    sitemap_host = (urlparse(sitemap_url).hostname or "").removeprefix("www.")
    site_host = (parsed_site.hostname or "").removeprefix("www.")

    if sitemap_host != site_host:
        print("External sitemap skipped")
        continue

    try:
        response = requests.get(
            sitemap_url, headers=headers, timeout=20
        )

        if response.status_code != 200:
            print("HTTP status:", response.status_code)
            continue

        print("HTTP status:", response.status_code)
        print("Final URL:", response.url)
        print("Content-Type:", response.headers.get("Content-Type"))
        root = ET.fromstring(response.content)

        if root.tag.endswith("sitemapindex"):
            links = root.findall(".//{*}sitemap/{*}loc")
            print("Sitemap index found")
            print("Child sitemaps:", len(links))

            product_sitemap_url = None
            for link in links:
                if link.text and "product-sitemap.xml" in link.text:
                    product_sitemap_url = link.text.strip()
                    break

            if product_sitemap_url:
                print("Reading:", product_sitemap_url)

                product_response = requests.get(
                    product_sitemap_url,
                    headers=headers,
                    timeout=(10, 45)
                )

                product_response.raise_for_status()

                product_root = ET.fromstring(product_response.content)
                product_links = product_root.findall(".//{*}url/{*}loc")

                print("Product page URLs:", len(product_links))

                for link in product_links[:5]:
                    print(" ", link.text)

                # product_url = None

                # if product_links:
                #     product_url = product_links[0].text

                #     print("\nTesting first product:", product_url)

                #     product_data = fetch_site(product_url)

                #     print("Fetch status:", product_data["status"])

                #     if product_data["status"] == "OK":
                #         soup = BeautifulSoup(product_data["html"], "html.parser")

                #         title = soup.find("title")

                #         print(
                #             "Product page title:",
                #             title.get_text(strip=True) if title else "Missing"
                #         )
                #     else:
                #         print("Reason:", product_data["message"])
                products = []
                product_urls = []

                for link in product_links:
                    if link.text and "/products/" in link.text:
                        # product_url = link.text.strip()
                        # break
                        product_urls.append(link.text.strip())

                    if len(product_urls) == 3:
                        break

                for product_url in product_urls:
                    print("\nAnalyzing:", product_url)

                    product_data = fetch_site(product_url)

                    if product_data["status"] == "OK":
                        product = extract_product(product_data["html"])

                        if product:
                            product["url"] = product_url
                            products.append(product)

                            print("Name:", product["name"])
                            print("Price:", product["price"])
                            print("Availability:", product["availability"])

                        else:
                            print("Product JSON-LD not found :(")
                    else:
                        print("Fetch status:", product_data["status"])

                    sleep(1)

                print("\nTotal products collected:", len(products))

                if products:
                    df = pd.DataFrame(products)

                    print("\n PRODUCT TABLE:")
                    print(df[["name", "price", "currency", "availability"]].to_string(index=False))

                    df["price"] = pd.to_numeric(df["price"], errors="coerce")

                    print("\nPRICE STATISTICS:")
                    print("Products with prices:", df["price"].count())
                    print("Minimum price:", df["price"].min())
                    print("Maximum price:", df["price"].max())
                    print("Average price:", round(df["price"].mean(), 2))
                    print("Median price:", df["price"].median())

                    #Shop name
                    df["store"] = parsed_site.netloc

                    #New folder for reports
                    folder = Path("reports")
                    folder.mkdir(exist_ok=True)

                    #CSV
                    shop_name = parsed_site.netloc.replace(".", "_")
                    csv_path = folder / f"products_{shop_name}.csv"

                    #Saving
                    df.to_csv(csv_path, index=False, encoding="utf-8-sig")

                    print("\nCSV saved:", csv_path.resolve())

                else:
                    print("No product to analyze")
        
                # if product_url:
                #     print("\nTesting product:", product_url)
        
                #     product_data = fetch_site(product_url)
        
                #     print("Fetch status:", product_data["status"])
        
                #     if product_data["status"] == "OK":
                #         # soup = BeautifulSoup(product_data["html"], "html.parser")
                #         # title = soup.find("title")
        
                #         # print(
                #         #     "Product page title:",
                #         #     title.get_text(strip=True) if title else "Missing"
                #         # )
                #         product = extract_product(product_data["html"])

                #         if product:
                #             print("Product found!")
                #             print("Name:", product["name"])
                #             print("SKU:", product["sku"])
                #             print("Price:", product["price"])
                #             print("Currency:", product["currency"])
                #             print("Availability:", product["availability"])
                #         else:
                #             print("Product JSON-LD not found :(")
                    
                #     else:
                #         print("Reason:", product_data["message"])
                # else:
                #     print("No product URL found")

        elif root.tag.endswith("urlset"):
            links = root.findall(".//{*}url/{*}loc")
            print("URL sitemap found")
            print("Page URLs:", len(links))

            sample_positions = [0, 10, 100, 500, 1000, 5000, 10000]

            for position in sample_positions:
                if position < len(links):
                    print(f"URL #{position}: {links[position].text}")

            if len(links) > 500:
                product_url = links[500].text

                if product_url:
                    print("\nTesting URL from sitemap:", product_url)

                    product_data = fetch_site(product_url)
                    print("Fetch status:", product_data["status"])

                    if product_data["status"] == "OK":
                        soup = BeautifulSoup(
                            product_data["html"], "html.parser"
                        )

                        scripts = soup.find_all(
                            "script",
                            attrs={"type": "application/ld+json"}
                        )

                        print("JSON-LD blocks found:", len(scripts))

                        product = extract_product(product_data["html"])

                        if product:
                            print("Product found!")
                            print("Name:", product["name"])
                            print("SKU:", product["sku"])
                            print("Price:", product["price"])
                            print("Currency:", product["currency"])
                            print("Availability:", product["availability"])
                        else:
                            print("Product JSON-LD not found :(")

                    else:
                        print("Reason:", product_data["message"])

        else:
            print("Unknown XML structure:", root.tag)
            continue

        # for link in links[:5]:
        #     print(" ", link.text)

    except (requests.RequestException, ET.ParseError) as error:
        print("Cannot read sitemap:", error)