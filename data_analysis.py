from pathlib import Path
from urllib.parse import urlparse
import pandas as pd
import re

def extract_weight_kg(name):
    if not isinstance(name, str):
        return None

    matches = re.findall(
        r"(?<!\w)(\d+(?:[.,]\d+)?)\s*(kg|g)\b",
        name,
        flags=re.IGNORECASE
    )

    if len(matches) != 1:
        return None

    amount, unit = matches[0]

    weight = float(amount.replace(",", "."))

    if weight <= 0:
        return None

    if unit.lower() == "g":
        weight = weight / 1000

    return weight

def analyze_products(products, shop_url):
    if not products:
        print("No products to analyze")
        return None

    df = pd.DataFrame(products)

    #Convert prices to numbers
    df["price"] = pd.to_numeric(
        df["price"],
        errors="coerce"
    )

    #Weight
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

    #Calculate price statistics
    print("\nPRICE STATISTICS:")
    print("Total products:", len(df))
    print("Products with prices:", df["price"].count())
    print("Minimum:", df["price"].min())
    print("Maximum:", df["price"].max())
    print("Average:", round(df["price"].mean(), 2))
    print("Median:", df["price"].median())

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
