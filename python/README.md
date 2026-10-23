# Infografia

Una pàgina amb les conclusions principals de l'informe, en el format del *World Economic Report* original.

![Informe econòmic de Catalunya](output/informe_economic_catalunya.png)

Descàrrega: [PNG](output/informe_economic_catalunya.png) · [PDF](output/informe_economic_catalunya.pdf)

## Com llegir-la

| Gràfic | Què mostra |
|---|---|
| El PIB ha crescut… | Evolució del PIB de cada àmbit (2011–2023, preus corrents), apilat |
| La població ha passat… | Evolució de la població de cada àmbit (1981–2025), apilat |
| On es produeix la riquesa… | Cada bombolla és una comarca, i la mida indica la població. Per sota de la línia discontínua, la renda dels residents és baixa respecte del PIB que s'hi produeix. Per sobre, és alta |
| Índex socioeconòmic territorial | Punts de cada àmbit per sobre o per sota de Catalunya (= 100) |
| La indústria impulsa el PIB… | Cada punt és una comarca. El color indica l'IST: blau per sobre de la mitjana i taronja per sota |

Els textos de la dreta es calculen a partir de les dades. Si les dades s'actualitzen, les xifres canvien soles.

## Tornar-la a generar

Des de l'arrel del repositori, executa `python src/extract.py`. Després obre [`informe_economic.ipynb`](informe_economic.ipynb) i executa totes les cel·les (*Kernel → Restart & Run All*). La imatge i el PDF es desen a `output/`.
