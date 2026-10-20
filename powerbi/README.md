# Versió Power BI / Fabric

Fa servir les mateixes dades de l'Idescat que la versió Python, però organitzades com a **model en estrella** per a Power BI. El projecte es desa en format `.pbip` perquè es pugui versionar amb Git.

## 1. Generar el model

Des de l'arrel del repositori, després de `python src/extract.py`:

```bash
python src/model.py
```

Crea `data/model/`:

| Taula | Gra | Contingut |
|---|---|---|
| `dim_territori` | comarca | `comarca_code`, `comarca`, `ambit_code`, `ambit` (jerarquia Àmbit → Comarca) |
| `dim_any` | any | 1981–2026 |
| `dim_indicador` | indicador | nom, unitat i com s'agrega (suma o mitjana ponderada) |
| `dim_sector` | sector | agricultura, indústria, construcció, serveis |
| `fact_indicadors` | comarca × any × indicador | PIB, població, IST, renda i components de l'IST |
| `fact_vab` | comarca × any × sector | VAB en milions € |
| `ref_oficial` | àmbit/Catalunya × any × indicador | valors oficials per conciliar (taula desconnectada) |

## 2. Carregar-lo a Power BI Desktop

1. Crea un paràmetre `RutaRepo` (text) amb la ruta de la carpeta del repositori.
2. Per a cada CSV, una consulta en blanc amb aquest patró (canvia el nom del fitxer):

```powerquery
let
    Origen = Csv.Document(
        File.Contents(RutaRepo & "\data\model\dim_territori.csv"),
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Capçaleres = Table.PromoteHeaders(Origen, [PromoteAllScalars = true]),
    Tipus = Table.TransformColumnTypes(Capçaleres, {{"comarca_code", type text}})
in
    Tipus
```

Compte amb dues coses:
- `Encoding = 65001` (UTF-8). Sense això, els accents surten malament.
- `comarca_code` ha de ser **text**. Si el converteixes en nombre, perds el zero inicial ("01" passa a 1) i les relacions fallen.

3. Relacions (totes 1 → *, filtre en una sola direcció):

| Des de | Cap a |
|---|---|
| `dim_territori[comarca_code]` | `fact_indicadors[comarca_code]`, `fact_vab[comarca_code]` |
| `dim_any[any]` | `fact_indicadors[any]`, `fact_vab[any]` |
| `dim_indicador[indicador_code]` | `fact_indicadors[indicador_code]` |
| `dim_sector[sector_code]` | `fact_vab[sector_code]` |

`ref_oficial` queda desconnectada. Es farà servir a la fase de control de qualitat.

4. Mesures: obre [`measures.dax`](measures.dax) a la **Visualització de consultes DAX**, executa-ho i fes clic a *Actualitza el model amb els canvis*.

## 3. Comprovar les mesures

La consulta `EVALUATE` del final de `measures.dax` ha de donar aquests valors, calculats amb pandas a partir dels mateixos CSV. Cada mesura agafa l'últim any amb dades: PIB i VAB 2023, població 2025, renda 2023 i IST 2024.

| Àmbit | PIB (M€) | Població | PIB per habitant (€) | Renda (€) | IST | Pes indústria |
|---|---:|---:|---:|---:|---:|---:|
| Alt Pirineu i Aran | 2.227 | 77.215 | 29.357 | 15.806 | 97,0 | 9,3% |
| Camp de Tarragona | 19.444 | 564.162 | 35.495 | 15.091 | 95,6 | 28,9% |
| Comarques Centrals | 14.136 | 431.254 | 33.675 | 15.826 | 96,1 | 34,0% |
| Comarques Gironines | 25.854 | 814.218 | 32.616 | 15.097 | 90,3 | 19,8% |
| Metropolità | 202.615 | 5.134.100 | 40.579 | 17.232 | 102,1 | 16,3% |
| Penedès | 13.586 | 530.997 | 26.430 | 15.711 | 98,8 | 24,7% |
| Ponent | 12.750 | 381.531 | 34.127 | 14.557 | 89,0 | 20,9% |
| Terres de l'Ebre | 5.865 | 190.648 | 31.688 | 13.342 | 86,2 | 34,1% |

## 4. Pàgines de l'informe

| Pàgina | Contingut |
|---|---|
| 1. Resum | Les 5 visualitzacions de la infografia Python, amb un segmentador d'any i d'àmbit |
| 2. Comarques | Taula i mapa per comarca, amb detall Àmbit → Comarca |
| 3. Mercat laboral | Atur i afiliacions (pendent: cal afegir les taules a `src/sources.py`) |

## 5. Desar com a projecte

*Fitxer → Desa com a → Projecte de Power BI (.pbip)*, dins d'aquesta carpeta (`powerbi/`). Abans, activa a *Opcions → Característiques en versió preliminar* els formats **TMDL** i **PBIR**. Així el model i l'informe es desen com a text llegible i Git pot mostrar els canvis línia a línia. El `.gitignore` ja exclou els fitxers locals (`.pbi/localSettings.json`, `.pbi/cache.abf`).

## 6. Fabric (més endavant)

Durant els 60 dies de la prova gratuïta: un Lakehouse amb `src/` executat des d'un notebook (bronze = JSON crus, silver = `data/processed`, gold = `data/model`) i un model semàntic en mode Direct Lake. No s'ha d'activar la prova fins que aquesta versió de Desktop estigui acabada.
