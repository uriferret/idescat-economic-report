# Informe econòmic de Catalunya · dades de l'Idescat

On es genera la riquesa a Catalunya, on viu la gent i com hi viu. Aquest informe compara les **42 comarques i l'Aran** i els **8 àmbits territorials** amb dades oficials de l'[Idescat](https://www.idescat.cat).

És una adaptació a Catalunya del projecte *World Economic Report* de Maven Analytics, que fa la mateixa comparació entre països amb dades del Banc Mundial.

![Infografia](python/output/informe_economic_catalunya.png)

## Què hi trobaràs

| Versió | Per a què | Com obrir-la |
|---|---|---|
| [**Infografia**](python/) | Llegir les conclusions en una sola pàgina | Obre la imatge [PNG](python/output/informe_economic_catalunya.png) o el [PDF](python/output/informe_economic_catalunya.pdf) |
| [**Informe de Power BI**](powerbi/) | Explorar les dades per any, àmbit i comarca | Obre `powerbi/informe_economic.pbip` amb Power BI Desktop. Les instruccions són a [`powerbi/README.md`](powerbi/) |
| [**Dashboard web**](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW) | Consultar l'informe des del navegador, sense instal·lar res | Obre [l'enllaç](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW) |

## Principals conclusions

- **El PIB ha crescut un 42%** entre el 2011 i el 2023, en termes nominals. L'àmbit Metropolità genera el 68% del PIB i hi viu el 63% de la població.
- **El Penedès és l'àmbit que més ha crescut** en població des del 1981 (+120%).
- **On es produeix la riquesa no és on viu la gent.** La Ribera d'Ebre té el PIB per habitant més alt de Catalunya, per l'energia nuclear, però una renda per persona per sota de la mitjana. El Garraf és la segona comarca en renda i una de les últimes en PIB per habitant.
- **El PIB per habitant no explica el benestar.** Entre comarques, la correlació amb l'índex socioeconòmic territorial (IST) és pràcticament nul·la (r = 0,01). La renda, en canvi, hi està molt relacionada (r = 0,85).
- **On es treballa no sempre és on es viu.** Només 6 comarques tenen més llocs de treball que residents afiliats; el Barcelonès és la que en té més (1,39 llocs per cada resident afiliat, el 2025). Al Moianès i al Garraf, en canvi, n'hi ha menys de la meitat.

## Dashboard web

[Obre el dashboard](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW)

- **Pestanyes:** *Resum* (PIB, població, renda i IST per àmbit), *Comarques* (taula de les 42 comarques i l'Aran) i *Laboral* (afiliacions, atur i desplaçaments per feina).
- **Detall:** passa el ratolí per sobre de qualsevol gràfic per veure'n els valors.
- **Taula de comarques:** escriu el nom d'una comarca o d'un àmbit per filtrar-la, i fes clic a una capçalera per ordenar-la.
- **Fonts:** el panell *Sources* mostra d'on surt cada xifra, de quina data és i com s'ha calculat. També permet descarregar les dades en CSV.
- **Tema:** la pàgina es mostra en clar o en fosc segons la configuració del teu dispositiu.

**Privadesa i accés.** El dashboard és només de lectura: qui el visita no hi pot fer canvis. La pàgina no demana cap dada ni desa res al navegador del visitant, i no es connecta a cap sistema extern. Totes les dades són estadístiques públiques de l'Idescat i no contenen informació personal.

## Actualitzar les dades

Les dades es descarreguen de l'API de l'Idescat i es poden tornar a generar amb Python 3.10 o posterior:

```bash
pip install -r requirements.txt
python src/extract.py   # descarrega les taules de l'Idescat a data/processed/
python src/model.py     # prepara les taules de l'informe de Power BI a data/model/
```

Després, a la infografia, executa el notebook [`python/informe_economic.ipynb`](python/informe_economic.ipynb). A l'informe de Power BI, fes clic a **Actualitza**.

`data/processed/qa_report.md` resumeix la revisió de les dades descarregades: valors buits, dades provisionals i si les comarques sumen el total de cada àmbit.

## Fitxers

```
python/   infografia (notebook i imatge final)
powerbi/  informe de Power BI
data/     dades descarregades i preparades
src/      descàrrega i preparació de les dades
config/   correspondència entre comarques i àmbits territorials
tests/    proves
```

## Fonts

Dades: **[Idescat](https://www.idescat.cat)**, Institut d'Estadística de Catalunya, a través de l'[API Taules v2](https://www.idescat.cat/dev/api/taules/): PIB territorial, estimacions de població, índex socioeconòmic territorial, afiliacions a la Seguretat Social i estimació mensual de la població activa. Les dades no s'han modificat. Cartografia: © Instituto Geográfico Nacional (CC BY 4.0).

Aquest projecte no té cap relació ni aval de l'Idescat.

## Autoria

**Oriol Ferret Cedó**, consultor de Business Intelligence · [LinkedIn](https://www.linkedin.com/in/oriol-ferret) · [GitHub](https://github.com/uriferret)

Desenvolupat amb l'ajuda de Claude (Anthropic) per al codi i la documentació. L'anàlisi, el disseny de l'informe i la validació de les dades són de l'autor.

Codi publicat amb llicència [MIT](LICENSE). Les dades són de l'Idescat i es regeixen per les seves [condicions d'ús](https://www.idescat.cat/dev/api/?lang=ca).

---

## English

# Catalonia Economic Report · Idescat data

Where wealth is generated in Catalonia, where people live, and how well they live. This report compares the **42 comarques (counties) and Aran** and the **8 territorial planning areas** using official data from [Idescat](https://www.idescat.cat), the Statistical Institute of Catalonia.

It is a Catalan adaptation of Maven Analytics' *World Economic Report*, which makes the same comparison across countries using World Bank data.

### What's inside

| Version | Use it to | How to open it |
|---|---|---|
| [**Infographic**](python/) | Read the main findings on a single page | Open the [PNG](python/output/informe_economic_catalunya.png) or the [PDF](python/output/informe_economic_catalunya.pdf) |
| [**Power BI report**](powerbi/) | Explore the data by year, area and comarca | Open `powerbi/informe_economic.pbip` with Power BI Desktop (free). Instructions in [`powerbi/README.md`](powerbi/) (in Catalan) |
| [**Web dashboard**](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW) | Browse the report in a web browser, nothing to install | Open [the link](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW) |

### Key findings

- **GDP grew by 42%** in nominal terms between 2011 and 2023. The Metropolitan area produces 68% of GDP and is home to 63% of the population.
- **Penedès is the fastest-growing area** in population since 1981 (+120%).
- **Wealth is not produced where people live.** Ribera d'Ebre has the highest GDP per capita in Catalonia, driven by nuclear power, yet its income per person is below average. Garraf ranks second in income and among the last in GDP per capita.
- **GDP per capita does not explain well-being.** Across comarques, its correlation with the territorial socioeconomic index (IST) is practically zero (r = 0.01), while income is strongly related to it (r = 0.85).
- **People don't always work where they live.** Only 6 comarques have more jobs than employed residents, led by Barcelonès (1.39 jobs per employed resident in 2025). In Moianès and Garraf there are fewer than half.

### Web dashboard

[Open the dashboard](https://claude.ai/artifact/F5mz53ZLQtgQfxVQYd6nZW) (in Catalan)

- **Tabs:** *Resum* (summary: GDP, population, income and IST by area), *Comarques* (table of all 42 comarques and Aran) and *Laboral* (employment, unemployment and commuting).
- **Details:** hover over any chart to see its values.
- **Comarques table:** type a comarca or area name to filter it, and click a column header to sort it.
- **Sources:** the *Sources* panel shows where each figure comes from, its date and how it was calculated, and lets you download the data as CSV.
- **Theme:** the page follows your device's light or dark setting.

**Privacy and access.** The dashboard is read-only: visitors cannot change it. The page asks for no data, stores nothing in the visitor's browser and connects to no external system. All data is public Idescat statistics with no personal information.

### Updating the data

Data is downloaded from the Idescat API and can be regenerated with Python 3.10 or later:

```bash
pip install -r requirements.txt
python src/extract.py   # downloads the Idescat tables into data/processed/
python src/model.py     # builds the Power BI tables in data/model/
```

Then run the notebook [`python/informe_economic.ipynb`](python/informe_economic.ipynb) for the infographic, or click **Refresh** in the Power BI report.

### Sources

Data: **[Idescat](https://www.idescat.cat)**, via the [Tables API v2](https://www.idescat.cat/dev/api/taules/): territorial GDP, population estimates, territorial socioeconomic index, Social Security affiliations and monthly labour force estimates. Data has not been modified. Maps: © Instituto Geográfico Nacional (CC BY 4.0). This project is not affiliated with or endorsed by Idescat.


### Author

**Oriol Ferret Cedó**, Business Intelligence Consultant · [LinkedIn](https://www.linkedin.com/in/oriol-ferret) · [GitHub](https://github.com/uriferret)

Built with the help of Claude (Anthropic) for code and documentation. The analysis, report design and data validation are the author's.

Code released under the [MIT](LICENSE) licence. Data belongs to Idescat and is subject to its [terms of use](https://www.idescat.cat/dev/api/?lang=en).
