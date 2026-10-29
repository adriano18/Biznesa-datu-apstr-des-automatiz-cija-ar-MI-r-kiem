import flet as ft
import asyncio
from fetch_sites import fetch_site
from seo_analyzer import analyze_seo
from excel_report import save_excel

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
        result
        )

    page.update()
    await page.window.center()
    page.window.visible = True
    page.update()

ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)