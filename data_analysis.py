"""Clean a sample of product records, calculate price metrics and export CSV.

The input is a list of dictionaries from product_collector. The output is
a Pandas DataFrame with numeric prices, extracted package weights and EUR/kg.
This is descriptive sample analysis, not a fair same-product price comparison."""

from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
import re

# STEP 1: Recognize a single package weight (kg or g) in a product title.
def extract_weight_kg(name):
    if not isinstance(name, str):
        return None

    matches = re.findall(
        r"(?<!\w)(\d+(?:[.,]\d+)?)\s*(kg|g)\b",
        name,
        flags=re.IGNORECASE
    )

    # Ambiguous or missing weights remain unknown rather than being guessed.
    if len(matches) != 1:
        return None

    amount, unit = matches[0]

    weight = float(amount.replace(",", "."))

    if weight <= 0:
        return None

    if unit.lower() == "g":
        weight = weight / 1000

    return weight

# STEP 2: Convert the collected records to a cleaned Pandas table.
def analyze_products(products, shop_url):
    if not products:
        print("No products to analyze")
        return None

    df = pd.DataFrame(products)

    #Convert prices to numbers
    # Invalid price strings become NaN and are excluded from numeric statistics.
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    #Weight
    # Unit comparison is possible only when a package weight is detected.
    df["weight_kg"] = df["name"].apply(extract_weight_kg)

    #Calculate unit price
    df["price_per_kg"] = (
        df["price"] / df["weight_kg"]
    ).round(2)

    #Add store information
    shop_name = urlparse(shop_url).netloc
    df["store"] = shop_name

    #Show the tble
    print("\nPRODUCT TABLE:")
    print(
        df[["name", "price", "weight_kg", "price_per_kg", "currency", "availability"]]
        .to_string(index=False)
    )

    # STEP 3: Describe this sample using summary statistics.
    #Calculate price statistics
    print("\nPRICE STATISTICS:")
    print("Total products:", len(df))
    print("Products with prices:", df["price"].count())
    print("Minimum:", df["price"].min())
    print("Maximum:", df["price"].max())
    print("Average:", round(df["price"].mean(), 2))
    print("Median:", df["price"].median())

    # STEP 4: Save UTF-8 CSV beside the project code for Excel and PDF.
    #Save CV
    folder = Path(__file__).resolve().parent / "reports"
    folder.mkdir(exist_ok=True)

    filename = shop_name.replace(".", "_")
    csv_path = folder / f"products_{filename}.csv"

    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig"
    )

    df.attrs["csv_path"] = str(csv_path.resolve())

    print("\nCSV saved:", csv_path.resolve())

    return df
