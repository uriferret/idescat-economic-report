# Validació de les dades

2026-11-09 18:48 UTC · 26 correctes, 0 amb incidències

- ✅ pib: suma de comarques = Catalunya. Diferència màxima 0.000%
- ✅ vab: suma de comarques = Catalunya. Diferència màxima 0.033%
- ✅ poblacio: suma de comarques = Catalunya. Diferència màxima 0.006%
- ✅ afiliats_res: suma de comarques = Catalunya (comptant els afiliats no residents a Catalunya o sense residència coneguda). Diferència màxima 0.001%
- ✅ PIB per habitant 2023 (PIB / població a 1 de juliol) = oficial a totes les comarques. Diferència màxima 0.03% (Alta Ribagorça)
- ✅ PIB per habitant 2023: totes les comarques amb valor oficial tenen valor calculat
- ✅ PIB per habitant de Catalunya 2023: 37,259 € (oficial 37,259 €)
- ✅ poblacio 2025S1: la diferència entre l'àmbit oficial i la suma de comarques l'expliquen els 12 municipis de config/municipis_ambit_diferent.csv (desviació màxima 0)
- ✅ afiliats_res 2026M09: la diferència entre l'àmbit oficial i la suma de comarques l'expliquen els 12 municipis de config/municipis_ambit_diferent.csv (desviació màxima 5)
- ✅ dim_territori: 43 comarques sense duplicats
- ✅ dim_territori: totes les comarques tenen àmbit
- ✅ fact_indicadors: sense files duplicades
- ✅ fact_indicadors: totes les comarques existeixen a dim_territori
- ✅ fact_vab: sense files duplicades
- ✅ fact_vab: totes les comarques existeixen a dim_territori
- ✅ fact_afiliacions_sector: sense files duplicades
- ✅ fact_afiliacions_sector: totes les comarques existeixen a dim_territori
- ✅ fact_ambit_oficial: 6 de 6 indicadors amb xifres oficials per àmbit
- ✅ dim_municipi: 947 municipis sense duplicats
- ✅ fact_municipis: sense files duplicades
- ✅ fact_municipis: tots els municipis existeixen a dim_municipi
- ✅ Atur registrat 2006-2025: els 947 municipis cada any (mínim 947)
- ✅ Atur registrat 2025: la suma dels municipis (324,351) és la de Catalunya a l'EMEX (325,084), menys els 199 municipis que el SEPE amaga («<5»): diferència 0.23%
- ✅ Atur registrat 2025: la mitjana anual de 5 municipis és la de l'EMEX (diferència màxima 0.00)
- ✅ Renda per municipi 2015-2023: almenys 900 municipis cada any (mínim 911)
- ✅ Renda per municipi: la mitjana dels municipis ponderada per població és la de Catalunya (diferència màxima 0.32%)

## Detall

### poblacio · 2025S1

```
àmbit  oficial - suma de comarques  municipis reassignats  diferència
 AT01                       4291.0                 4291.0         0.0
 AT06                       1126.0                 1126.0         0.0
 AT08                      -5417.0                -5417.0         0.0
```

### afiliats_res · 2026M09

```
àmbit  oficial - suma de comarques  municipis reassignats  diferència
 AT01                       1960.0                 1965.0        -5.0
 AT02                         -5.0                    0.0        -5.0
 AT05                          5.0                    0.0         5.0
 AT06                        305.0                  300.0         5.0
 AT08                      -2270.0                -2265.0        -5.0
```

### fact_ambit_oficial

```
indicador_code  min  max  count
       AFI_RES 2015 2025     88
   AFI_RG_LLOC 2020 2025     48
    AFI_RG_RES 2015 2025     88
           POP 2015 2025     88
     POP_16_64 2015 2025     88
       POP_JUL 2015 2024     80
```
### Atur registrat 2025 · SEPE i EMEX

```
municipi_code    EMEX    SEPE
        08019 63038.8 63038.8
        17079  4296.4  4296.4
        25120  6434.9  6434.9
        43148  6235.3  6235.3
        08305  1703.5  1703.5
```

### Renda per municipi · mitjana ponderada i Catalunya

```
 any  municipis  ponderada  Catalunya diferència
2015        914      12353    12326.0     +0.22%
2016        912      12735    12695.0     +0.32%
2017        911      13120    13082.0     +0.29%
2018        915      13682    13650.0     +0.24%
2019        912      14139    14107.0     +0.22%
2020        947      14180    14152.0     +0.19%
2021        945      14780    14748.0     +0.22%
2022        932      15542    15519.0     +0.15%
2023        927      16492    16461.0     +0.19%
```

