"""Create a two-page Latvian market sample report from product CSV exports.
Run: python market_report.py
Requires: pandas, matplotlib, reportlab
"""
from datetime import datetime
from html import escape
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import font_manager
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer, Image, PageBreak

ROOT = Path(__file__).resolve().parent
REPORT_DIR = ROOT / "reports"
REPORT_DIR.mkdir(exist_ok=True)
FILENAMES = ["products_suns_lv.csv", "products_www_zoocentrs_lv.csv"]


def read_products():

    frames = []

    for filename in FILENAMES:
        # Normal app: reports/<file>.csv. Also accept a CSV beside this script.
        path = REPORT_DIR / filename

        if not path.exists():
            path = ROOT / filename

        if not path.exists():
            raise FileNotFoundError(f"CSV not found: {filename}")
        
        data = pd.read_csv(path, encoding="utf-8-sig", dtype={"sku": "string"})

        for column in ("price", "weight_kg", "price_per_kg"):
            data[column] = pd.to_numeric(data[column], errors="coerce")

        data["availability_short"] = data["availability"].fillna("Unknown").astype(str).str.rsplit("/", n=1).str[-1]
        data["store_short"] = data["store"].astype(str).str.removeprefix("www.")
        frames.append(data)

    return pd.concat(frames, ignore_index=True)


def create_price_chart(data, target):
    names = []

    for _, product in data.iterrows():
        short_name = str(product["name"]).split(" sausā ")[0][:35]
        names.append(f"{product['store_short']}: {short_name}")

    fig, ax = plt.subplots(figsize=(9.7, 3.7))
    positions = list(range(len(data)))
    ax.barh(positions, data["price_per_kg"].to_list())
    ax.set_yticks(positions, labels=names)
    ax.invert_yaxis()
    ax.set_xlabel("Cena par kilogramu (EUR/kg)")
    ax.set_title("Cena par kilogramu atlasītajām precēm")
    ax.grid(axis="x", alpha=0.18)
    ax.set_axisbelow(True)
    fig.subplots_adjust(left=0.39, right=0.97, top=0.86, bottom=0.15)
    fig.savefig(target, dpi=170)

    plt.close(fig)


def create_stock_chart(data, target):
    counts = data.groupby("store_short")["availability_short"].apply(lambda col: int((col == "InStock").sum()))
    totals = data.groupby("store_short").size()
    fig, ax = plt.subplots(figsize=(7.8, 2.5))
    bars = ax.bar(counts.index.tolist(), counts.to_list(), width=0.5)

    for bar, shop in zip(bars, counts.index):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.08,
                f"{counts[shop]}/{totals[shop]}", ha="center")
        
    ax.set_ylim(0, max(4, int(totals.max()) + 1))
    ax.set_ylabel("Preces ar InStock statusu")
    ax.set_title("Pieejamība atlasītajās precēs")
    ax.grid(axis="y", alpha=0.18)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(target, dpi=170)

    plt.close(fig)


def make_pdf(data, price_chart, stock_chart, target, category):
    # DejaVu includes Latvian characters; register it for ReportLab PDF text.
    font_path = font_manager.findfont("DejaVu Sans")

    pdfmetrics.registerFont(TTFont("DejaVuReport", font_path))

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name="ReportTitle", fontName="DejaVuReport", fontSize=17, leading=23, spaceAfter=12))
    styles.add(ParagraphStyle(name="ReportHead", fontName="DejaVuReport", fontSize=11, leading=16, spaceBefore=9, spaceAfter=7))
    styles.add(ParagraphStyle(name="ReportBody", fontName="DejaVuReport", fontSize=8.5, leading=13, spaceAfter=7))
    styles.add(ParagraphStyle(name="ReportCell", fontName="DejaVuReport", fontSize=7.1, leading=10))
    styles.add(ParagraphStyle(name="ReportSmall", fontName="DejaVuReport", fontSize=7.3, leading=11, textColor=colors.HexColor("#475569")))

    doc = SimpleDocTemplate(str(target), pagesize=A4, leftMargin=19*mm,
                            rightMargin=19*mm, topMargin=17*mm, bottomMargin=17*mm)
    story = [Paragraph("E-komercijas tirgus analīze", styles["ReportTitle"]),
             Paragraph("Kategorija: " + escape(category) + " | Parauga analīze | " + datetime.now().strftime("%d.%m.%Y"), styles["ReportBody"]),
             Paragraph("1. Izlases kopsavilkums", styles["ReportHead"])]

    summary = [["Veikals", "Preces", "Vid. cena (EUR)", "Mediāna (EUR/kg)", "InStock"]]

    for shop, group in data.groupby("store_short", sort=False):
        avg = group["price"].mean()
        unit = group["price_per_kg"].median()
        stocked = int((group["availability_short"] == "InStock").sum())
        summary.append([shop, str(len(group)), f"{avg:.2f}" if pd.notna(avg) else "N/A",
                        f"{unit:.2f}" if pd.notna(unit) else "N/A", f"{stocked}/{len(group)}"])
        
    table = Table(summary, colWidths=[41*mm, 18*mm, 34*mm, 43*mm, 25*mm], hAlign="LEFT")

    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7EDF3")),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuReport"),
        ("FONTSIZE", (0, 0), (-1, -1), 7.7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, -1), (-1, -1), 0.5, colors.HexColor("#CBD5E1")),
    ]))

    story.append(table)
    story.append(Spacer(1, 8*mm))
    story.append(Paragraph("2. Cenu vizualizācija", styles["ReportHead"]))
    story.append(Image(str(price_chart), width=170*mm, height=77*mm))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("Svarīgi: veikaliem atlasīti atšķirīgi zīmoli un produktu veidi. "
                           "EUR/kg palīdz salīdzināt iepakojuma izmērus, bet nepierāda vienādu preču cenu priekšrocību.", styles["ReportSmall"]))
    story.append(Spacer(1, 9*mm))
    story.append(Paragraph("Izlases novērojumi", styles["ReportHead"]))
    story.append(Paragraph(
        "Analīze balstīta uz atlasītajām precēm. "
        "Veikaliem var atšķirties zīmoli, produktu veidi "
        "un iepakojuma izmēri. "
        "Cenas par kilogramu palīdz salīdzināt iepakojumus, "
        "taču tiešai konkurentu cenu salīdzināšanai "
        "nepieciešamas identiskas preces.",
        styles["ReportBody"]
    ))

    story.append(PageBreak())
    story.append(Paragraph("3. Atlasīto preču detalizācija", styles["ReportHead"]))
    rows = [[Paragraph(s, styles["ReportCell"]) for s in
             ("Veikals", "Produkts", "Cena EUR", "Svars kg", "EUR/kg", "Pieejamība")]]
    
    for _, product in data.iterrows():

        def fmt(value):
            return f"{value:.2f}" if pd.notna(value) else "—"
        
        rows.append([
            Paragraph(escape(str(product["store_short"])), styles["ReportCell"]),
            Paragraph(escape(str(product["name"])), styles["ReportCell"]),
            Paragraph(fmt(product["price"]), styles["ReportCell"]),
            Paragraph(fmt(product["weight_kg"]), styles["ReportCell"]),
            Paragraph(fmt(product["price_per_kg"]), styles["ReportCell"]),
            Paragraph(escape(str(product["availability_short"])), styles["ReportCell"]),
        ])

    details = Table(rows, colWidths=[24*mm, 71*mm, 17*mm, 17*mm, 17*mm, 27*mm], repeatRows=1, hAlign="LEFT")

    details.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E7EDF3")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("LEFTPADDING", (0, 0), (-1, -1), 4),
        ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))

    story.append(details)

    story.append(Spacer(1, 7*mm))
    story.append(Paragraph("4. Pieejamība", styles["ReportHead"]))
    story.append(Image(str(stock_chart), width=151*mm, height=48*mm))
    story.append(Spacer(1, 4*mm))
    story.append(Paragraph("Metodika un ierobežojumi: dati iegūti no veikalu XML sitemap un Product JSON-LD; "
                           "izlase ir maza (3 preces katrā veikalā) un nav reprezentatīva. "
                           "PreOrder nav tas pats, kas InStock. Lai salīdzinātu konkurentu cenas, "
                           "jāsapāro identiski produkti ar vienādu zīmolu, modeli un iepakojumu.", styles["ReportSmall"]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont("DejaVuReport", 8)
        canvas.drawRightString(A4[0] - 19*mm, 11*mm, f"Lapa {doc.page}")
        canvas.restoreState()

    doc.build(story, onFirstPage=footer, onLaterPages=footer)


def main(category="sausā kaķu barība"):
    data = read_products()
    price_chart = REPORT_DIR / "chart_price_per_kg.png"
    stock_chart = REPORT_DIR / "chart_availability.png"
    pdf = REPORT_DIR / "market_analysis.pdf"

    create_price_chart(data, price_chart)
    create_stock_chart(data, stock_chart)
    make_pdf(data, price_chart, stock_chart, pdf, category)
    print(f"PDF saved: {pdf}")
    print(f"Charts saved: {price_chart.name}, {stock_chart.name}")

    return str(pdf)

if __name__ == "__main__":
    main()
