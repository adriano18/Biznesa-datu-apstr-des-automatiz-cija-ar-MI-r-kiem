"""Flet desktop interface for the ecommerce analysis coursework.

Two actions: SEO audit -> Excel and category sample -> CSV/PDF.
Network scraping runs in worker threads so the GUI stays responsive.
The exact-product matching module is not yet connected to this UI."""

import flet as ft
import asyncio
from fetch_sites import fetch_site
from seo_analyzer import analyze_seo
from excel_report import save_excel
from sitemap_reader import get_candidate_urls
from product_collector import collect_products
from data_analysis import analyze_products
import pandas as pd
from market_report import main as create_market_report
from urllib.parse import urlparse

# STEP 1: Discover category URLs, scrape products and prepare the shop summary.
def build_product_summary(shop_url, keywords):
    urls = get_candidate_urls(shop_url, max_urls=15, keywords=keywords)

    products = collect_products(urls, limit=3)

    df = analyze_products(products, shop_url)

    if df is None:
        raise ValueError("No products found for selected category")

    prices = df["price"].dropna()

    # average = (
    #     f"{prices.mean():.2f} EUR"
    #     if not prices.empty
    #     else "Not available"
    # )

    unit_prices = df["price_per_kg"].dropna()

    in_stock = (
        df["availability"]
        .fillna("")
        .astype(str)
        .str.endswith("/InStock")
        .sum()
    )

    lines = [
        f"Shop: {shop_url}",
        f"Products collected: {len(df)}",
        f"In stock: {in_stock}/{len(df)}",
        (
            f"Average price: {prices.mean():.2f} EUR"
            if not prices.empty else "Average price: N/A"
        ),
        (
            f"Median price/kg: {unit_prices.median():.2f} EUR"
            if not unit_prices.empty else "Median price/kg: N/A"
        ),
        "",
        "PRODUCTS:"
    ]

    for _, product in df.iterrows():
        name = str(product["name"])

        price = (
            f"{product['price']:.2f} EUR"
            if pd.notna(product["price"])
            else "N/A"
        )

        unit_price = (
            f"{product['price_per_kg']:.2f} EUR/kg"
            if pd.notna(product["price_per_kg"])
            else "N/A"
        )

        availability = (
            str(product["availability"]).rsplit("/", 1)[-1]
            if pd.notna(product["availability"])
            else "Unknown"
        )

        lines.append(
            f"{name}\n"
            f"{price} | {unit_price} | {availability}\n"
        )

    lines.append(
        f"CSV saved: {df.attrs.get('csv_path', 'Not available')}"
    )

    return "\n".join(lines)

# STEP 2: Build the Flet window and connect button event handlers.
async def main(page: ft.Page):
    page.title = "Ecommerce Market Analyzer"
    page.padding = 30
    page.window.width = 900
    page.window.height = 550
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.scroll = ft.ScrollMode.AUTO

    shop_a = ft.TextField(
        label="Shop A URL", 
        value="https://suns.lv/", 
        width=500
        )
    
    shop_b = ft.TextField(
        label="Shop B URL", 
        value="https://www.zoocentrs.lv/", 
        width=500
        )

    category_input = ft.TextField(
        label="Product category keywords",
        value="sausa-bariba, kakiem",
        width=500
    )

    result = ft.Text("", size=14, weight="bold")

    products_result = ft.Text("")

    # def run_analysis(e):
    #     url_a = shop_a.value.strip()
    #     url_b = shop_b.value.strip()

    #     if not url_a.startswith("https://") or not url_b.startswith("https://"):
    #         result.value = "Please enter valid URLs starting with 'https://'"
    #     else:
    #         result.value = f"Analyzing:\nShop A: {url_a}\nShop B: {url_b}"
    #         print("Shop A URL:", url_a)
    #         print("Shop B URL:", url_b)

    # SEO route: convert the fetched HTML audit into readable lines.
    def format_report(shop_name, data):
        if data["status"] != "OK":
            return f"{shop_name}: {data["status"]} - {data["message"]}"
        audit = analyze_seo(data["html"])
        lines = [f"--- {shop_name} SEO Audit ---"]

        for name, item in audit.items():
            lines.append(f"{name} : {item["status"]} | {item['value']}")

        return "\n".join(lines)

    # Product route: process the two shops one after another.
    async def run_products(e):
        urls = [shop_a.value.strip(), shop_b.value.strip()]

        # User-entered comma-separated category terms become URL filter keywords.
        keywords = [
            word.strip()
            for word in category_input.value.split(",")
            if word.strip()
        ]

        if not all(urls):
            products_result.value = "Enter both shop URLs."
            page.update()
            return

        reports = []
        all_ok = True

        products_result.value = "Starting product analysis..."
        page.update()

        for url in urls:
            products_result.value = f"Analyzing {url}..."
            page.update()

            try:
                summary = await asyncio.to_thread(
                    build_product_summary, url, keywords
                )

            except Exception as error:
                all_ok = False
                summary = f"{url}\nError: {error}"

            reports.append(summary)

        # PDF uses fixed CSV filenames for these two shops in this version.
        #PDF script
        shops = {urlparse(url).netloc.lower() for url in urls}
        supported_shops = {"suns.lv", "www.zoocentrs.lv"}

        if all_ok and shops == supported_shops:
            products_result.value = (
                "\n\n".join(reports) + "\n\nGenerating PDF..."
            )

            page.update()

            try:
                pdf_path = await asyncio.to_thread(
                    create_market_report,
                    category_input.value.strip()
                )
                reports.append(f"PDF saved: {pdf_path}")
            except Exception as error:
                reports.append(f"PDF generation error: {error}")

        elif not all_ok:
            reports.append(
                "PDF not generated: product analysis was incomplete."
            )
        else:
            reports.append(
                "PDF export currently supports suns.lv "
                "and www.zoocentrs.lv only."
            )

        products_result.value = "\n\n".join(reports)
        page.update()

    # SEO route: fetch both homepages, compare checks and save an Excel file.
    async def run_analysis(e):
        url_a = shop_a.value.strip()
        url_b = shop_b.value.strip()

        if not url_a.startswith("https://") or not url_b.startswith("https://"):
            result.value = "Please enter valid URLs starting with 'https://'"
            page.update()
            return

        result.value = f"Downloading {shop_a.label}"
        page.update()

        data_a = await asyncio.to_thread(fetch_site, url_a)

        result.value = f"Downloading {shop_b.label}"
        page.update()

        data_b = await asyncio.to_thread(fetch_site, url_b)

        report_a = await asyncio.to_thread(format_report, "SHOP A", data_a)
        report_b = await asyncio.to_thread(format_report, "SHOP B", data_b)

        result.value = "Generating Excel report..."
        page.update()

        excel_path = await asyncio.to_thread(
            save_excel, url_a, data_a, url_b, data_b
        )

        result.value = (
            report_a + "\n\n" + report_b
            + f"\n\nExcel saved: {excel_path}"
        )

        page.update()

    # Add input fields, actions and the two separate result areas to the window.
    page.add(
        ft.Text("Ecommerce Market Analyzer!", size=30, weight="bold"), 
        ft.Text("SEO Audit and Market Analysis Tool", size=20),
        shop_a, 
        shop_b, 
        category_input,
        ft.Button("Run Analysis", on_click=run_analysis),
        ft.Button(
            content="Analyze Products",
            on_click=run_products
        ),
        products_result,
        result
        )

    page.update()
    await page.window.center()
    page.window.visible = True
    page.update()

ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)