# LEGACY PRACTICE: this file uses hard-coded sample HTML and does not run in Flet.
# See seo_analyzer.py for the active SEO checker.
from bs4 import BeautifulSoup
import json
from urllib.parse import urlparse

html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Food for Cats</title>
    <link rel="canonical" href="https://example.com/products/field-notebook/" />
    <meta name="robots" content="index, follow">
    <script type="application/ld+json">
    {
  "@context": "https://schema.org",
  "@type": "Organization",
  "@id": "https://example.com/#organization",
  "name": "Example Studio",
  "url": "https://example.com/",
  "logo": "https://example.com/logo.png",
  "sameAs": ["https://www.linkedin.com/company/example-studio"]
}
    </script>
    <script type="application/ld+json">
    {
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "Cat Food",
  "image": "https://example.com/notebook.jpg",
  "sku": "FN-01",
  "offers": {
    "@type": "Offer",
    "priceCurrency": "EUR",
    "price": "24.00",
    "availability": "https://schema.org/InStock",
    "url": "https://example.com/products/field-notebook"
  }
}
    </script>
</head>
<body>
    <h1>Cat Food</h1>
    <h1>Additional heading</h1>
    <p>This is a sample paragraph.</p>
    <div class="content">
        <p>Another paragraph inside a div.</p> 
    </div>
    <h2>Subheading</h2>
    <p>Yet another paragraph.</p>
    <table>
        <tr>
            <th>Header 1</th>
            <th>Header 2</th>
        </tr>
        <tr>
            <td>Row 1, Cell 1</td>
            <td>Row 1, Cell 2</td>
        </tr>
    </table>
    <dl>
        <dt>Term 1</dt>
        <dd>Definition 1</dd>
    </dl>

</body>
</html>

"""

soup = BeautifulSoup(html, 'html.parser')

title = soup.find('title')
description = soup.find('meta', attrs={'name': 'description'})
canonical = soup.find('link', attrs={'rel': 'canonical'})
robots = soup.find('meta', attrs={'name': 'robots'})
schema_block = soup.find_all('script', attrs={'type': 'application/ld+json'})

product_name = ""
product_url = ""

for block in schema_block:
    try:
        schema_data = json.loads(block.get_text())
        print("Schema.org type:", schema_data.get('@type', 'No type found'))

        if schema_data.get('@type') == "Product":
            product_name = schema_data.get('name', '')
            offers = schema_data.get('offers', {})
            product_url = offers.get('url', '')
    except json.JSONDecodeError:
        print("Invalid JSON in schema.org block")

h1 = soup.find('h1')
h1_count = len(soup.find_all('h1'))
h2 = soup.find('h2')
table = soup.find('table')
terms = soup.find_all('dt')

# '''print("Title:", title.text if title else "No title found")
# print("Description:", description['content'] if description else "No description found")
# print("Canonical:", canonical['href'] if canonical else "No canonical link found")
# print("Robots:", robots['content'] if robots else "No robots meta tag found")
# print("Schema.org blocks found:", len(schema_block))
# print("H1:", h1.text if h1 else "No H1 found")
# print("H1 count:", h1_count)
# print("H2:", h2.text if h2 else "No H2 found")
# print("Table:", "Table found" if table else "No table found")
# print("Terms:", [term.text for term in terms] if terms else "No terms found")

# print("\n--- SEO Check Summary ---")

# checks = {}

# # Check for Title
# if title and title.get_text().strip():
#     checks['Title'] = "Present"
# else:
#     checks['Title'] = "Missing"

# # Check for Meta Description
# if description and description.get('content', '').strip():
#     checks['Description'] = "Present"
# else:
#     checks['Description'] = "Missing"
# '''
# Check for Canonical Link
canonical_url = canonical.get('href', '').strip() if canonical else ''
parsed_url = urlparse(canonical_url)
# '''if not canonical_url:
#     checks['Canonical'] = "Missing or invalid"
# elif parsed_url.scheme in ("https", "http") and parsed_url.netloc and not parsed_url.fragment:
#     checks['Canonical'] = "Format OK"
# else:
#     checks['Canonical'] = "Check canonical URL format"


# # Check for Robots Meta Tag
# if robots and robots.get('content', '').strip():
#     checks['Robots'] = "Present"
# else:
#     checks['Robots'] = "Missing"

# print("\n--- Content Consistency Audit ---")'''
h1_text = h1.get_text(strip=True) if h1 else ""
# '''if not canonical_url or not product_url:
#     print("Canonical vs Product URL - Not checked")
# elif canonical_url.rstrip("/") == product_url.rstrip("/"):
#     print ("Canonical vs Product URL - matched")
# else:
#     print("Please review Canonical vs Product URL")
#     print("Canonical:", canonical_url)
#     print("Product URL", product_url)
# if not product_name or not h1_text:
#     print("Product name vs H1 - Not checked")
# elif product_name.casefold() == h1_text.casefold():
#     print("Product name vs H1 - matched")
#     print("H1:", h1_text)
#     print("Product name:", product_name)
# else:
#     print("Please review Product name vs H1")
# #Check for H1
# if h1_count == 0:
#     checks['H1'] = "Missing"
# elif h1_count > 1:
#     checks['H1'] = "Multiple H1 tags found"
# elif h1 and h1.get_text().strip():
#     checks['H1'] = "Present"
# else:
#     checks['H1'] = "Empty H1 tag found"

# issues_count = sum(1 for status in checks.values() if status not in ("Present", "Present and valid", "Format OK"))

# for name, status in checks.items():
#     print(f"{name}: {status}")

# print(f"\n--- SEO Issues Summary ---")
# print(f"Issues found: {issues_count}")

# print("\n--- SEO Check Summary for Optional Elements ---")

# optional_checks = {}

# # Check for H2
# if h2 and h2.get_text().strip():
#     optional_checks['H2'] = "Present"
# else:
#     optional_checks['H2'] = "Missing"

# # Check for dl and dt tags
# if soup.find('dl') and terms:
#     optional_checks['Definition List'] = "Present"
# else:
#     optional_checks['Definition List'] = "Missing"

# # Check for table
# if table:
#     optional_checks['Table'] = "Present"
# else:
#     optional_checks['Table'] = "Missing"

# missing_optional_count = sum(1 for status in optional_checks.values() if status != "Present")

# for name, status in optional_checks.items():
#     print(f"{name}: {status}")

# print(f"\n--- Optional Elements Summary ---")
# print(f"Missing optional elements: {missing_optional_count}")
# '''
print("\n--- Structured SEO Audit ---")

audit = {}

def add_check(name, status, value):
    audit[name] = {
        "status" : status,
        "value" : value
    }

#Title
if title and title.get_text(strip=True):
    audit["Title"] = {
        "status" : "OK",
        "value" : title.get_text(strip=True)
    }
else:
    audit["Title"] = {
            "status" : "ERROR",
            "value" : "Title is missing or empty"
    }

#Meta Description
if description and description.get("content", "").strip():
    audit["Description"] = {
        "status" : "OK",
        "value" : description.get("content", "").strip()
    }
else:
    audit["Description"] = {
            "status" : "REVIEW",
            "value" : "Description is missing or empty"
    }

#Canonical
if not canonical_url:
    audit["Canonical"] = {
        "status" : "REVIEW",
        "value" : "Canonical is missing or empty"
    }
elif parsed_url.scheme in ("https", "http") and parsed_url.netloc and not parsed_url.fragment:
    audit["Canonical"] = {
        "status": "OK",
        "value": canonical_url
    }

else:
    audit["Canonical"] = {
        "status": "REVIEW",
        "value": "Check canonical URL format"
    }

robots_value = robots.get("content", "").strip() if robots else ""
if not robots_value:
    add_check("Robots", "INFO", "Meta robots not specified")
elif "noindex" in robots_value.casefold() or robots_value.casefold() == "none":
    add_check("Robots", "REVIEW", robots_value)
else:
    add_check("Robots", "OK", robots_value)

# H1
if h1_count == 0:
    add_check("H1", "REVIEW", "No H1 found")
elif h1_count > 1:
    add_check("H1", "REVIEW", f"{h1_count} H1 tags found")
elif not h1_text:
    add_check("H1", "REVIEW", "H1 is empty")
else:
    add_check("H1", "OK", h1_text)


# H2 - optional
if h2 and h2.get_text(strip=True):
    add_check("H2", "INFO", h2.get_text(strip=True))
else:
    add_check("H2", "INFO", "Not present")


# HTML Table - optional
if table:
    add_check("Table", "INFO", "Present")
else:
    add_check("Table", "INFO", "Not present")


# Definition List - optional
if soup.find("dl") and terms:
    add_check("Definition List", "INFO", f"{len(terms)} terms found")
else:
    add_check("Definition List", "INFO", "Not present")


# Product name vs H1
if not product_name or not h1_text:
    add_check("Product vs H1", "NOT CHECKED", "Missing comparison data")
elif product_name.casefold() == h1_text.casefold():
    add_check("Product vs H1", "OK", "Names match")
else:
    add_check("Product vs H1", "REVIEW", f"{product_name} != {h1_text}")


# Canonical vs Product URL
if not canonical_url or not product_url:
    add_check("Canonical vs Product URL", "NOT CHECKED", "Missing URL")
elif canonical_url.rstrip("/") == product_url.rstrip("/"):
    add_check("Canonical vs Product URL", "OK", "URLs match in simplified comparison")
else:
    add_check("Canonical vs Product URL", "REVIEW", "URLs differ")

# Schema.org types
schema_types = []
invalid_json_count = 0

for block in schema_block:
    try:
        data = json.loads(block.get_text())

        if isinstance(data, dict):
            schema_type = data.get("@type")

            if schema_type:
                schema_types.append(schema_type)

    except json.JSONDecodeError:
        invalid_json_count += 1

if invalid_json_count > 0:
    add_check("Schema.org", "ERROR", f"{invalid_json_count} invalid JSON-LD blocks")
elif schema_types:
    add_check("Schema.org", "OK", ", ".join(schema_types))
else:
    add_check("Schema.org", "INFO", "No top-level Schema.org types found")

for name, result in audit.items():
    print(f"{name}: {result["status"]} | {result["value"]}")