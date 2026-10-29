import json
from urllib.parse import urlparse
from bs4 import BeautifulSoup

def analyze_seo(html):
    soup = BeautifulSoup(html, "html.parser")
    audit = {}

    def add_check(name, status, value):
        audit[name] = {"status" : status, "value" : str(value)}

    #Title
    title = soup.find("title")
    title_text = title.get_text(strip=True) if title else ""
    add_check("Title", "OK" if title_text else "ERROR", title_text or "Missing or empty")

    #Meta Description
    description = soup.find("meta", attrs={"name" : "description"})
    description_text = description.get("content", "").strip() if description else ""
    add_check("Description", "OK" if description_text else "REVIEW", description_text or "Missing or empty")

    #Canonical
    canonical = soup.find("link", rel="canonical")
    canonical_url = canonical.get("href", "").strip() if canonical else ""
    parsed = urlparse(canonical_url)

    if not canonical_url:
        add_check("Canonical", "REVIEW", "Not specified")
    elif parsed.scheme in ("https", "http") and parsed.netloc and not parsed.fragment:
        add_check("Canonical", "OK", canonical_url)
    else:
        add_check("Canonical", "REVIEW", canonical_url)

    #Robots
    robots = soup.find("meta", attrs={"name": "robots"})
    robots_text = robots.get("content", "").strip() if robots else ""

    if not robots_text:
        add_check("Robots", "INFO", "Not specified")
    elif "noindex" in robots_text.casefold() or robots_text.casefold() == "none":
        add_check("Robots", "REVIEW", robots_text)
    else:
        add_check("Robots", "OK", robots_text)

    #H1
    h1_tags = soup.find_all("h1")
    h1_text = h1_tags[0].get_text(strip=True) if h1_tags else ""

    if not h1_tags or not h1_text:
        add_check("H1", "REVIEW", "Missing or empty")
    elif len(h1_tags) > 1:
        add_check("H1", "REVIEW", f"{len(h1_tags)} H1 tags")
    else:
        add_check("H1", "OK", h1_text)

    #Optional HTML elements
    add_check("H2", "INFO", f"{len(soup.find_all('h2'))} tags")
    add_check("Tables", "INFO", f"{len(soup.find_all('table'))} tables")
    add_check("Definition Terms", "INFO", f"{len(soup.find_all('dt'))} terms")

    #Schema.org JSON-LD
    schema_types = []
    invalid_json = 0
    product_name = ""
    product_url = ""

    for script in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            data = json.loads(script.get_text())
        except json.JSONDecodeError:
            invalid_json += 1
            continue

        items = data if isinstance(data, list) else [data]

        for item in items:
            if not isinstance(item, dict):
                continue

            entities = item.get("@graph", [item])
            if not isinstance(entities, list):
                entities = [item]

            for entity in entities:
                if not isinstance(entity, dict):
                    continue

                types = entity.get("@type", [])
                if isinstance(types, str):
                    types = [types]
                if not isinstance(types, list):
                    types = []

                schema_types.extend(t for t in types if isinstance(t, str))

                if "Product" in types:
                    product_name = entity.get("name", "")
                    offers = entity.get("offers", {})
                    if isinstance(offers, dict):
                        product_url = offers.get("url", "")

    if invalid_json:
        add_check("Schema.org", "ERROR", f"{invalid_json} invalid JSON-LD blocks")
    elif schema_types:
        add_check("Schema.org", "OK", ", ".join(sorted(set(schema_types))))
    else:
        add_check("Schema.org", "INFO", "No supported JSON-LD types found")

    #Content consistency
    if product_name and h1_text:
        status = "OK" if product_name.casefold() == h1_text.casefold() else "REVIEW"
        add_check("Product vs H1", status, f"{product_name} / {h1_text}")
    else:
        add_check("Product vs H1", "NOT CHECKED", "Product data unavailable")

    if canonical_url and product_url:
        status = "OK" if canonical_url.rstrip("/") == product_url.rstrip("/") else "REVIEW"
        add_check("Canonical vs Product URL", status,
                  f"{canonical_url} / {product_url}")
    else:
        add_check("Canonical vs Product URL", "NOT CHECKED", "Product URL unavailable")

    return audit
