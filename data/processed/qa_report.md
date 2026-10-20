# Informe de qualitat de les dades

Extracció: 2026-10-20 15:00 UTC · Font: Idescat

## Resum per taula

- **pib/cat**: 42 files, 0 valors buits (0.0%) | períodes 2011–2024 (14), estats: {'p': 9}
- **pib/at**: 351 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 54}
- **pib/com**: 1716 files, 36 valors buits (2.1%) | períodes 2011–2023 (13), estats: {'p': 261, '..': 36}
- **vab/cat**: 65 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 10}
- **vab/at**: 585 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 90}
- **vab/com**: 2860 files, 60 valors buits (2.1%) | períodes 2011–2023 (13), estats: {'p': 435, '..': 60}
- **poblacio/cat**: 91 files, 0 valors buits (0.0%) | períodes 1981S1–2026S1 (91), estats: {'p': 2}
- **poblacio/at**: 801 files, 61 valors buits (7.6%) | períodes 1981S1–2025S1 (89), estats: {'..': 61}
- **poblacio/com**: 3916 files, 154 valors buits (3.9%) | períodes 1981S1–2025S1 (89), estats: {'..': 154}
- **ist/cat**: 10 files, 0 valors buits (0.0%) | períodes 2015–2024 (10), estats: {'p': 1}
- **ist/com**: 440 files, 9 valors buits (2.0%) | períodes 2015–2024 (10), estats: {'p': 44, '..': 9}
- **ist_indicadors/com**: 2580 files, 349 valors buits (13.5%) | períodes 2015–2024 (10), estats: {'..': 349, 'b': 126, 'p': 86}

## Mapatge comarca → àmbit

- ✅ Totes les comarques tenen àmbit assignat

## Suma de comarques = total d'àmbit

- ⚠️ pib: 13 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code source period_code CONCEPT   value  value_at  rel_diff
      AT06    pib        2023  GDP_ME 14136.0   13996.5  0.009967
      AT06    pib        2015  GDP_ME 10000.7    9909.1  0.009244
      AT06    pib        2012  GDP_ME  9461.7    9378.4  0.008882
      AT06    pib        2013  GDP_ME  9235.0    9154.0  0.008849
      AT06    pib        2011  GDP_ME  9605.9    9522.7  0.008737
- ⚠️ vab: 72 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code source period_code SEC_ACTIV_G   CONCEPT  value  value_at  rel_diff
      AT06    vab        2023           A GVA_M_EUR  191.8     185.7  0.032849
      AT06    vab        2023           F GVA_M_EUR  711.6     699.6  0.017153
      AT06    vab        2018           F GVA_M_EUR  726.4     715.5  0.015234
      AT06    vab        2019           F GVA_M_EUR  734.2     723.7  0.014509
      AT06    vab        2020           F GVA_M_EUR  566.0     558.1  0.014155
- ⚠️ poblacio: 207 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code   source period_code   SEX CONCEPT    value  value_at  rel_diff
      AT06 poblacio      2011S1 TOTAL     POP 394317.0  512615.0  0.230774
      AT06 poblacio      2010S2 TOTAL     POP 393545.0  511582.0  0.230729
      AT06 poblacio      2010S1 TOTAL     POP 392795.0  510572.0  0.230677
      AT06 poblacio      2009S2 TOTAL     POP 391777.0  508975.0  0.230263
      AT06 poblacio      2009S1 TOTAL     POP 390759.0  507379.0  0.229848
