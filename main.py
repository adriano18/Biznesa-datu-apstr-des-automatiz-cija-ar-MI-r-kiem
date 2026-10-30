import flet as ft
import asyncio
from fetch_sites import fetch_site
from seo_analyzer import analyze_seo
from excel_report import save_excel
from sitemap_reader import get_candidate_urls
from product_collector import collect_products
from data_analysis import analyze_products

def build_product_summary(shop_url):
    urls = get_candidate_urls(shop_url, max_urls=10)

    products = collect_products(urls, limit=3)

    df = analyze_products(products, shop_url)

    if df is None:
        return f"{shop_url}\nNo products found."

    prices = df["price"].dropna()

    average = (
        f"{prices.mean():.2f} EUR"
        if not prices.empty
        else "Not available"
    )

    in_stock = (
        df["availability"]
        .fillna("")
        .astype(str)
        .str.endswith("InStock")
        .sum()
    )

    return (
        f"Shop: {shop_url}\n"
        f"Products collected: {len(df)}\n"
        f"Average price: {average}\n"
        f"In stock: {in_stock}\n"
        f"CSV report saved in reports"
    )

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

    result = ft.Text("Result will be displayed here", size=14, weight="bold")

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

    def format_report(shop_name, data):
        if data["status"] != "OK":
            return f"{shop_name}: {data["status"]} - {data["message"]}"
        audit = analyze_seo(data["html"])
        lines = [f"--- {shop_name} SEO Audit ---"]

        for name, item in audit.items():
            lines.append(f"{name} : {item["status"]} | {item['value']}")

        return "\n".join(lines)

    async def run_products(e):
        urls = [shop_a.value.strip(), shop_b.value.strip()]

        if not all(urls):
            products_result.value = "Enter both shop URLs."
            page.update()
            return

        products_result.value = "Starting product analysis..."
        page.update()

        reports = []

        for url in urls:
            products_result.value = f"Analyzing {url}..."
            page.update()

            try:
                summary = await asyncio.to_thread(
                    build_product_summary, url
                )
            except Exception as error:
                summary = f"{url}\nError: {error}"

            reports.append(summary)

        products_result.value = "\n\n".join(reports)
        page.update()

    async def run_analysis(e):
        url_a = shop_a.value.strip()
        url_b = shop_b.value.strip()

        if not url_a.startswith("https://") or not url_b.startswith("https://"):
            result.value = "Please enter valid URLs starting with 'https://'"
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

    page.add(
        ft.Text("Ecommerce Market Analyzer!", size=30, weight="bold"), 
        ft.Text("SEO Audit and Market Analysis Tool", size=20),
        shop_a, 
        shop_b, 
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