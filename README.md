# Informe econòmic de Catalunya · dades de l'Idescat

Adaptació a Catalunya del projecte *World Economic Report* (Maven Analytics): en lloc de països i regions del món amb dades del Banc Mundial, compara les **comarques** i els **àmbits territorials** de Catalunya amb dades oficials de l'**API de l'Idescat**.

> **Estat:** en construcció. Fase 1: extracció de dades i controls de qualitat.

## Preguntes de l'informe

| # | Pregunta | Dades |
|---|---|---|
| 1 | Com ha evolucionat el PIB de cada àmbit territorial? | PIB territorial (2011–2023) |
| 2 | Com ha crescut la població de cada àmbit? | Estimacions de població (1981–) |
| 3 | On es produeix la riquesa i on viu la gent? | PIB per habitant vs. renda per persona, per comarca |
| 4 | Quin és el nivell socioeconòmic de cada territori? | Índex socioeconòmic territorial (IST) |
| 5 | L'estructura productiva explica la riquesa? | Pes de la indústria al VAB vs. PIB per habitant |

## Dues versions

| Carpeta | Eines | Resultat |
|---|---|---|
| [`claude/`](claude/) | Python (pandas, matplotlib, seaborn) | Infografia d'una pàgina, com l'original |
| [`powerbi/`](powerbi/) | Power BI Desktop (`.pbip`) · Microsoft Fabric | Informe interactiu |

Totes dues comparteixen la mateixa capa de dades (`src/`).

## Estructura

```
src/            client de l'API, catàleg de taules, extracció i controls de qualitat
config/         correspondència comarca → àmbit territorial
data/raw/       respostes JSON de l'API (no es versionen)
data/processed/ taules netes en CSV + informe de qualitat
claude/         versió Python
powerbi/        versió Power BI / Fabric
tests/          proves del parser JSON-stat (sense connexió)
```

## Com executar-ho

```bash
pip install -r requirements.txt
python src/extract.py        # descarrega les dades i genera data/processed/
python -m pytest tests       # proves
```

`data/processed/qa_report.md` resumeix els controls: comarques sense àmbit, si la suma de comarques quadra amb el total de cada àmbit, valors buits i dades provisionals.

## Notes metodològiques

- **Canvis comarcals:** el Moianès (2015) i el Lluçanès (2023) són comarques noves, cosa que trenca les sèries comarcals llargues. Els àmbits segueixen el Pla territorial vigent (8 àmbits, amb el Penedès).
- **PIB vs. renda:** el PIB es comptabilitza on es produeix; la renda, on resideixen les persones.

## Font i atribució

Dades: **[Idescat](https://www.idescat.cat)**, Institut d'Estadística de Catalunya, via l'[API Taules v2](https://www.idescat.cat/dev/api/taules/). Les dades no s'han modificat. Aquest projecte no té cap relació ni aval de l'Idescat.
