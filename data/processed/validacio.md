# Validació de les dades

2026-10-24 19:16 UTC · 18 correctes, 0 amb incidències

- ✅ pib: suma de comarques = Catalunya. Diferència màxima 0.000%
- ✅ vab: suma de comarques = Catalunya. Diferència màxima 0.033%
- ✅ poblacio: suma de comarques = Catalunya. Diferència màxima 0.006%
- ✅ afiliats_res: suma de comarques = Catalunya (comptant els afiliats sense municipi assignat). Diferència màxima 0.001%
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
