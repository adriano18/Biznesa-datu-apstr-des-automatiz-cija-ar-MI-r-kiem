import flet as ft

async def main(page: ft.Page):
    page.title = "Ecommerce Market Analyzer"
    page.padding = 30
    page.windows_width = 900
    page.window_height = 550
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

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

    result = ft.Text("Result will be displayed here", size=20, weight="bold")

    def run_analysis(e):
        url_a = shop_a.value.strip()
        url_b = shop_b.value.strip()

        if not url_a.startswith("https://") or not url_b.startswith("https://"):
            result.value = "Please enter valid URLs starting with 'https://'"
        else:
            result.value = f"Analyzing:\nShop A: {url_a}\nShop B: {url_b}"
            print("Shop A URL:", url_a)
            print("Shop B URL:", url_b)

    page.add(
        ft.Text("Ecommerce Market Analyzer!", size=30, weight="bold"), 
        ft.Text("SEO Audit and Market Analysis Tool", size=20),
        shop_a, 
        shop_b, 
        ft.Button("Run Analysis", on_click=run_analysis),
        result
        )

    page.update
    await page.window.center()
    page.window.visible = True
    page.update()

ft.run(main, view=ft.AppView.FLET_APP_HIDDEN)