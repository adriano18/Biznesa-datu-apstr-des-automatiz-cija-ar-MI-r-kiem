from pathlib import Path
from urllib.parse import urlparse
import pandas as pd

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

    #Add store information
    shop_name = urlparse(shop_url).netloc
    df["store"] = shop_name

    #Show the tble
    print("\nPRODUCT TABLE:")
    print(
        df[["name", "price", "currency", "availability"]]
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
    folder = Path("reports")
    folder.mkdir(exist_ok=True)

    filename = shop_name.replace(".", "_")
    csv_path = folder / f"products_{filename}.csv"

    df.to_csv(
        csv_path,
        index=False,
        encoding="utf-8-sig"
    )

    print("\nCSV saved:", csv_path.resolve())

    return df
