# E-komercijas tirgus analizators — projekta skaidrojums

## 1. Projekta mērķis
Python darbvirsmas lietotne **Ecommerce Market Analyzer** apkopo un apstrādā publiski pieejamu interneta veikalu informāciju. Mērķis ir parādīt procesu automatizāciju: no ievades URL līdz SEO pārbaudei, preču izlasei, cenu statistikai un atskaitēm.

## 2. Lietotāja ievade un rezultāts
- **Shop A URL / Shop B URL** — divu veikalu sākumlapu adreses.
- **Product category keywords** — kategorijas atslēgvārdi URL filtrēšanai (piemēram, `sausa-bariba, kakiem`).
- **Run Analysis** — SEO diagnostika un `seo_comparison_*.xlsx`.
- **Analyze Products** — nelielas kategorijas preču izlases apkopošana un `products_*.csv`; konkrētajam veikalu pārim papildus tiek ģenerēts `market_analysis.pdf` un PNG diagrammas.

## 3. Datu apstrādes soļi
1. `main.py` — Flet saskarne paņem lietotāja ievadītos URL un atslēgvārdus.
2. `sitemap_reader.py` — `robots.txt`, XML `sitemapindex`/`urlset`, kategorijas atslēgvārdu filtrs.
3. `product_collector.py` — ierobežotā apjomā lejupielādē kandidātadreses, izmantojot `fetch_sites.py`.
4. `product_parser.py` — no `Product` JSON-LD izgūst preces nosaukumu, SKU, cenu, valūtu un pieejamību; ja iespējams, arī zīmolu un GTIN.
5. `data_analysis.py` — Pandas: cenu pārveidošana par skaitļiem, svara noteikšana no nosaukuma, EUR/kg, vidējā cena, mediāna un CSV.
6. `market_report.py` — no CSV izveido divas diagrammas un latvisku PDF ar tabulu un lapas numuriem.
7. `seo_analyzer.py` + `excel_report.py` — neatkarīgs SEO diagnostikas ceļš uz Excel.

**Svarīgi:** `market_comparison.py` ir atsevišķi sagatavots modulis identisku preču salīdzināšanai pēc GTIN vai precīzi normalizēta nosaukuma un iepakojuma. Tā pārbaudes ir `test_market_comparison.py`. Pašreizējā GitHub `main.py` versijā šis modulis **vēl nav pieslēgts Flet pogai**. Nevajag uzdot par gatavu funkciju lietotāja saskarnē.

## 4. Failu orientieris
| Fails | Loma |
|---|---|
| `main.py` | Lietotāja saskarne un divas pogas |
| `fetch_sites.py` | HTTP pieprasījumi, `robots.txt`, statusi |
| `sitemap_reader.py` | Preču kandidātu URL atrašana |
| `product_parser.py` | Product JSON-LD parsēšana |
| `product_collector.py` | Preču atlase un lejupielāde |
| `data_analysis.py` | Pandas un CSV |
| `seo_analyzer.py`, `excel_report.py` | SEO un XLSX |
| `market_report.py` | Grafiki un PDF |
| `market_comparison.py` | Identisku preču salīdzināšanas modulis (neintegrēts GUI) |
| `test_market_comparison.py` | Pieci bezsaistes vienību testi |
| `sitemap_analyzer.py`, `seo_check.py` | Vēsturiskie mācību eksperimenti |
| `test_ikea_sitemap.py` | Atsevišķs IKEA Latvijas sitemap pārbaudes piemērs |

## 5. Darbināšana
Windows / PowerShell projekta mapē, aktivizētajā `.venv`:

```powershell
python -m pip install "flet[all]" requests beautifulsoup4 pandas openpyxl matplotlib reportlab
flet run main.py
```

Salīdzināšanas moduļa bezsaistes testi:

```powershell
python -m unittest -v test_market_comparison
```

Atsevišķa salīdzināšanas Excel izmēģināšana ar diviem CSV failiem `reports/`:

```powershell
python market_comparison.py
```

Tiešie `sitemap_analyzer.py` un `test_ikea_sitemap.py` testi izmanto internetu un ir domāti izpētei, nevis automātiskajai bezsaistes testu kopai.

## 6. Ierobežojumi un pareiza interpretācija
- Parasti tiek atlasītas **trīs preces no katra veikala**. Tā nav visa sortimenta analīze; izlase nav reprezentatīva.
- Kategorija sākotnēji tiek noteikta pēc atslēgvārdiem URL; iespējami kļūdaini iekļāvumi un izlaidumi.
- Preču cenu salīdzināšanai nepieciešami **identiski produkti un vienādi iepakojumi**. Atšķirīgu zīmolu vidējās cenas nevar pasludināt par viena veikala cenu priekšrocību.
- EUR/kg tiek aprēķināts tikai tad, ja nosaukumā identificēts viens nepārprotams svars; tas neder visām preču kategorijām.
- `InStock`, `PreOrder`, `OutOfStock` nāk no strukturētajiem datiem; statuss var mainīties.
- SEO `OK` nav Google indeksācijas vai pozīciju garantija.
- Pašreizējais `market_report.py` lasa **divu konkrētu zooveikalu CSV failus**; tas vēl nav vispārīgs PDF eksports jebkurai veikalu kombinācijai.
- Cenu dati nav pārdošanas dati; peļņu, uzcenojumu, piegādes izmaksas vai pieprasījumu šī versija neaprēķina.
- Saites uz IKEA produktiem ir pārbaudītas atsevišķā testā; IKEA vēl nav pilnībā integrēta vispārīgajā kategoriju atlasē.

## 7. Kā sekot attīstībai
Programmas galvenajos Python failos ir `# STEP` komentāri, kas paskaidro apstrādes secību. Šis dokuments raksturo **pašreizējo stāvokli**, bet Git vēsture saglabā iepriekšējos izstrādes posmus.

**Tālākie darbi:** pieslēgt `market_comparison.py` Flet saskarnei; ģenerēt PDF no lietotāja faktiski izvēlētajiem veikaliem; pievienot pārbaudes tukšām/nepareizām ievadēm un lielākām, daudzveidīgām izlasēm.
