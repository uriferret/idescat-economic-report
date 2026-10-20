# Versió Power BI

Informe de Power BI amb les mateixes dades de l'Idescat que la versió Python, organitzades com a **model en estrella**. Està desat en format `.pbip` (model en TMDL, informe en PBIR), perquè Git pugui versionar-ne cada canvi.

> **Estat:** model semàntic i mesures fets i validats. Pàgines de l'informe en construcció.

## Com obrir-lo

1. Obre `informe_economic.pbip` amb Power BI Desktop.
2. Si et demana credencials per a `raw.githubusercontent.com`, tria **Anònim** amb nivell de privacitat **Públic**.
3. Fes clic a **Actualitza**.

Les dades es llegeixen de `data/model/` d'aquest repositori a GitHub (paràmetre `RutaDades`). Per treballar amb fitxers locals, canvia el paràmetre per la ruta de la carpeta `data\model\` acabada en `\`.

## Model

| Taula | Gra | Contingut |
|---|---|---|
| `dim_territori` | comarca | comarca i àmbit territorial (jerarquia Àmbit → Comarca) |
| `dim_any` | any | 1981–2026 |
| `dim_indicador` | indicador | nom, unitat i com s'agrega |
| `dim_sector` | sector | agricultura, indústria, construcció, serveis |
| `fact_indicadors` | comarca × any × indicador | PIB, població, IST, renda i components de l'IST |
| `fact_vab` | comarca × any × sector | VAB en milions € |
| `ref_oficial` | àmbit/Catalunya × any × indicador | valors oficials, per conciliar (desconnectada) |

Les dimensions filtren els fets en una sola direcció (1 → *). Les taules es generen amb `python src/model.py`.

## Decisions de disseny

- **Fets a nivell de comarca.** Els àmbits i Catalunya s'obtenen sumant comarques, així tota la sèrie (1981–2025) fa servir la mateixa divisió de 8 àmbits. Respecte de les xifres oficials per àmbit, la diferència és inferior a l'1%, perquè alguns municipis pertanyen a un àmbit diferent del de la seva comarca.
- **Indicadors no additius.** Per a un àmbit o per a Catalunya, l'IST i la renda es calculen com la mitjana de les comarques ponderada per la població del mateix any.
- **Últim any amb dades.** Si el context inclou diversos anys (per exemple, una targeta sense filtre d'any), cada mesura mostra l'últim any disponible. El PIB per habitant fa servir el mateix any per al PIB i per a la població.
- Cada mesura té la seva **descripció** al model, que es veu en passar el ratolí per sobre al panell *Data*.

## Validació

La consulta `Validacio` de la vista de consultes DAX ha de donar els mateixos valors que pandas a partir dels mateixos CSV. Cada mesura agafa l'últim any amb dades: PIB i VAB 2023, població 2025, renda 2023 i IST 2024.

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

## Pàgines

| Pàgina | Contingut | Estat |
|---|---|---|
| 1. Resum | Les 5 visualitzacions de la infografia Python, amb segmentadors d'any i d'àmbit | pendent |
| 2. Comarques | Taula i mapa per comarca, amb detall Àmbit → Comarca | pendent |
| 3. Mercat laboral | Atur i afiliacions | pendent |

## Com s'ha construït

- **Power Query:** una funció `fnCsv` llegeix cada CSV en UTF-8 des de la ruta del paràmetre `RutaDades` (URL de GitHub o carpeta local). Cada taula és una crida a la funció amb els tipus de columna explícits. Els codis de comarca es carreguen com a text, per conservar el zero inicial.
- **Configuració regional:** anglès (Estats Units), perquè els CSV fan servir el punt com a separador decimal.
- **Mesures:** es van escriure i provar amb `DEFINE MEASURE` a la vista de consultes DAX abans d'afegir-les al model.
