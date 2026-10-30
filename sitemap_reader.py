"""Find candidate product-page URLs from a shop XML sitemap.

Supports sitemapindex and urlset, checks robots.txt for sitemap locations,
and filters links using category keywords in the URL.
IMPORTANT: URL keyword matching is preliminary, not product classification.
The flat-sitemap fallback chooses a small sample, not the whole assortment."""

import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

headers = {
        "User-Agent" : "EcommerceAuditAnalyzerBot/0.1"
    }

# STEP 1: Validate the store URL and normalize the category search words.
def get_candidate_urls(shop_url, max_urls=10, keywords=None):
    parsed = urlparse(shop_url.strip())

    if parsed.scheme not in ("http", "https") or not parsed.hostname:
        raise ValueError("Enter a valid shop URL")

    base_url = f"{parsed.scheme}://{parsed.netloc}"
    shop_host = parsed.hostname.removeprefix("www.")

    keywords = [
        word.strip().lower().replace(" ", "-")
        for word in (keywords or [])
        if word.strip()
    ]

    # Safety boundary: only accept URLs belonging to the requested shop host.
    def same_shop(url):
        parsed_url = urlparse(url)

        return (
            parsed_url.scheme in ("http", "https")
            and (parsed_url.hostname or "").removeprefix("www.")
            == shop_host
        )

    # STEP 2: Download XML and reject HTML responses or cross-host redirects.
    def read_xml(url):
        if not same_shop(url):
            return None

        try:
            response = requests.get(
                url,
                headers=headers,
                timeout=(10,45)
            )

            if response.status_code != 200:
                return None

            if not same_shop(response.url):
                return None

            content_type = response.headers.get(
                "Content-Type", ""
            ).lower()

            if "html" in content_type:
                return None

            return ET.fromstring(response.content)

        except (requests.RequestException, ET.ParseError):
            return None

    # STEP 3: Look for Sitemap: declarations in robots.txt.
    robots_response = requests.get(
        base_url + "/robots.txt",
        headers=headers,
        timeout=(10,20)
    )

    if robots_response.status_code == 200:
        sitemap_urls = [
            line.split(":", 1)[1].strip()
            for line in robots_response.text.splitlines()
            if line.lower().startswith("sitemap:")
        ]
    elif robots_response.status_code == 404:
        sitemap_urls = []
    else:
        raise RuntimeError("Cannot verify robots.txt")

    if not sitemap_urls:
        sitemap_urls = [
            base_url + "/sitemap.xml",
            base_url + "/sitemap_index.xml",
            base_url + "/wp-sitemap.xml"
        ]

    # STEP 4: Filter sitemap URLs; categories may still appear in the result.
    def select_urls(root):
        links = root.findall(".//{*}url/{*}loc")

        urls = [
            link.text.strip()
            for link in links
            if link.text and same_shop(link.text.strip())
        ]

        #Filter URLs by selected category
        if keywords:
            return [
                url for url in urls
                if all(word in url.lower() for word in keywords)
            ]

        #suns
        product_urls = [
            url for url in urls
            if "/products/" in url
        ]

        if product_urls:
            return product_urls

        #zoo
        start = len(urls) // 25
        return urls[start:start + max_urls]

    # STEP 5: Read a bounded number of child maps and deduplicate URLs.
    results = []

    for sitemap_url in sitemap_urls[:5]:
        root = read_xml(sitemap_url)

        if root is None:
            continue

        # try:
        #     response = requests.get(
        #         sitemap_url,
        #         headers=headers,
        #         timeout=(10,45)
        #     )

        #     if response.status_code != 200:
        #         continue

        #     content_type = response.headers.get("Content-Type", "").lower()

        #     if "html" in content_type:
        #         print("Expected XML, received HTML:", response.url)
        #         continue

        #     root = ET.fromstring(response.content)

        if root.tag.endswith("sitemapindex"):
            child_links = root.findall(
                ".//{*}sitemap/{*}loc"
            )

            # product_sitemaps = [
            #     link.text.strip()
            #     for link in child_links
            #     if link.text and "product" in link.text.lower()
            # ]

            # if not product_sitemaps:
            #     continue

            child_urls = [
                link.text.strip()
                for link in child_links
                if link.text and "product" in link.text.lower()
            ]

            for child_url in child_urls[:20]:
                child_root = read_xml(child_url)

                if child_root is None:
                    continue

                if not child_root.tag.endswith("urlset"):
                    continue

                selected = select_urls(child_root)

                for url in selected:
                    if url not in results:
                        results.append(url)

                    if len(results) >= max_urls:
                        return results
                    
        elif root.tag.endswith("urlset"):
            selected = select_urls(root)

            for url in selected:
                if url not in results:
                    results.append(url)

                if len(results) >= max_urls:
                    return results
                
    # No matching candidates in the inspected portion of the sitemap.
    return results

    #         child_host = (
    #             urlparse(child_url).hostname or ""
    #         ).removeprefix("www.")

    #         if child_host != shop_host:
    #             continue

    #         response = requests.get(
    #             child_url,
    #             headers=headers,
    #             timeout=(10,45)
    #         )

    #         response.raise_for_status()

    #         root = ET.fromstring(response.content)

    #     if not root.tag.endswith("urlset"):
    #         continue

    #     links = root.findall(".//{*}url/{*}loc")

    #     urls = [
    #         link.text.strip()
    #         for link in links
    #         if link.text
    #     ]

    #     #Identify products in URLs
    #     product_urls = [
    #         url for url in urls
    #         if "/products/" in url
    #     ]

    #     if product_urls:
    #         return product_urls[:max_urls]

    #     #Testing
    #     start = len(urls) // 25
    #     return urls[start:start + max_urls]

    #     # except (requests.RequestException, ET.ParseError):
    #     #     continue

    # return[]