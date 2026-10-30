# Ecommerce Market Analyzer
## Procesa apraksts

### 1. Īss procesa apraksts
Programma apkopo divu interneta veikalu publiskos SEO un preču datus, aprēķina cenu statistiku un sagatavo atskaites.

### 2. Procesa gaita
Izveidoju Python programmu ar Flet saskarni, kurā ievada divu veikalu adreses un kategorijas atslēgvārdus. Programma atrod lapas ar XML sitemap, pārbauda piekļuvi un nolasa preču datus no HTML un JSON-LD.

Ar Pandas tiek apstrādātas cenas, iepakojumu svars un pieejamība. Atsevišķi var palaist SEO pārbaudi. Rezultātus saglabā CSV un Excel failos, kā arī PDF atskaitē ar diagrammām. Identisku preču salīdzināšanas modulis ir izveidots, bet tā pieslēgšana Flet saskarnei vēl jāpabeidz.

**Procesa shēma**  
Ievade → sitemap → preču lapas → datu attīrīšana → statistika → CSV, Excel, PDF

### 3. Ievades dati
Divu veikalu URL, kategorijas atslēgvārdi, XML sitemap un preču lapu HTML/JSON-LD dati. Preču atlases apjoms ir ierobežots.

### 4. Izejas dati
SEO pārbaudes Excel fails, katra veikala preču CSV, cenu un pieejamības diagrammas un PDF atskaite. Atsevišķs modulis var veidot arī identisku preču salīdzinājuma Excel.

### 5. Ierobežojumi
Dati ir atkarīgi no veikalu pieejamības un lapu struktūras. Atlasītās preces neatspoguļo visu sortimentu. Ne vienmēr ir norādīts svars vai cena. Dažādu zīmolu vidējās cenas nav tieši salīdzināmas. Pašreizējais PDF eksports ir pielāgots diviem testētajiem zooveikaliem.

### 6. Iesaistītās puses
Programmas lietotājs, interneta veikalu sistēmas, Python programma un kursa vadītājs. Izstrādē izmantoju arī MI kā palīgu koda skaidrošanai, rakstīšanai un kļūdu labošanai. Rezultātus pārbaudīju ar praktiskiem izmēģinājumiem.

### 7. Automatizācijas riski
Vietņu struktūras izmaiņas, lēni pieprasījumi, `robots.txt` ierobežojumi, nepareizi vai novecojuši dati un kļūdaina dažādu produktu salīdzināšana. Riskus mazina pieprasījumu limiti, kļūdu apstrāde un pārbaudes pirms secinājumiem.

### 8. Veicamie uzdevumi bez automatizācijas
1. Izvēlēties divus veikalus un vienu salīdzināmu kategoriju.
2. Atvērt produktu lapas un pierakstīt cenas, svaru un pieejamību.
3. Attīrīt datus un aprēķināt cenu par kilogramu.
4. Sagatavot tabulu, diagrammas un atskaiti.
5. Manuāli pārbaudīt, vai salīdzinātie produkti tiešām ir vienādi.

### 9. Automatizācijas uzdevumi

| Uzdevums | Paskaidrojums | Ievade un izeja | Ierobežojumi |
|---|---|---|---|
| URL atrašana | Nolasīt sitemap un atlasīt kategorijas saites | Veikala URL, atslēgvārdi → saišu saraksts | Ne visos URL ir kategorijas nosaukums |
| Preču iegūšana | Nolasīt Product JSON-LD | Preces HTML → nosaukums, cena, svars, pieejamība | Dati var trūkt, jāpārbauda robots.txt |
| Datu analīze | Attīrīt cenas un aprēķināt EUR/kg, vidējo un mediānu | Preču dati → Pandas tabula, CSV | Svars var būt nezināms |
| Atskaišu veidošana | Sagatavot SEO Excel, diagrammas un PDF | Pārbaudītie dati → XLSX, PNG, PDF | Lielākām izlasēm jāpielāgo PDF |
| Preču salīdzināšana | Salīdzināt tikai vienādu produktu cenas | Divas preču tabulas → sakritības un cenu starpība | Jāsakrīt GTIN vai nosaukumam un iepakojumam |

### 10. Testa dati
Jāpārbauda `suns.lv` un `zoocentrs.lv` ar vienādas kategorijas precēm, tukšs vai nepareizs URL, lapa bez Product JSON-LD, dažādi atlases limiti, pieprasījuma noildze, `InStock` un `OutOfStock`. Salīdzināšanas testos jāiekļauj identiskas preces, atšķirīgi svari un konfliktējoši GTIN. IKEA sitemap izmantoju kā papildu piemēru.

### Tālākā attīstība
Pieslēgt preču sakritību meklēšanu Flet saskarnei, uzlabot kategoriju un zīmolu atlasi, rādīt statistiku atsevišķos blokos un veidot PDF jebkuram izvēlētam veikalam un preču skaitam.
