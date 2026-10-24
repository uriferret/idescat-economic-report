# Informe de qualitat de les dades

Extracció: 2026-10-24 21:11 UTC · Font: Idescat

## Resum per taula

- **pib/cat**: 42 files, 0 valors buits (0.0%) | períodes 2011–2024 (14), estats: {'p': 9}
- **pib/at**: 351 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 54}
- **pib/com**: 1716 files, 36 valors buits (2.1%) | períodes 2011–2023 (13), estats: {'p': 261, '..': 36}
- **pib_volum/cat**: 26 files, 0 valors buits (0.0%) | períodes 2000–2025 (26), estats: {'p': 3}
- **vab/cat**: 65 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 10}
- **vab/at**: 585 files, 0 valors buits (0.0%) | períodes 2011–2023 (13), estats: {'p': 90}
- **vab/com**: 2860 files, 60 valors buits (2.1%) | períodes 2011–2023 (13), estats: {'p': 435, '..': 60}
- **poblacio/cat**: 91 files, 0 valors buits (0.0%) | períodes 1981S1–2026S1 (91), estats: {'p': 2}
- **poblacio/at**: 801 files, 61 valors buits (7.6%) | períodes 1981S1–2025S1 (89), estats: {'..': 61}
- **poblacio/com**: 3916 files, 154 valors buits (3.9%) | períodes 1981S1–2025S1 (89), estats: {'..': 154}
- **ist/cat**: 10 files, 0 valors buits (0.0%) | períodes 2015–2024 (10), estats: {'p': 1}
- **ist/com**: 440 files, 9 valors buits (2.0%) | períodes 2015–2024 (10), estats: {'p': 44, '..': 9}
- **ist_indicadors/com**: 2580 files, 349 valors buits (13.5%) | períodes 2015–2024 (10), estats: {'..': 349, 'b': 126, 'p': 86}
- **afiliats_res/cat**: 110 files, 0 valors buits (0.0%) | períodes 2012M03–2026M09 (110), estats: {'p': 1}
- **afiliats_res/at**: 1100 files, 0 valors buits (0.0%) | períodes 2012M03–2026M09 (110), estats: {'p': 10}
- **afiliats_res/com**: 4950 files, 82 valors buits (1.7%) | períodes 2012M03–2026M09 (110), estats: {'..': 82, 'p': 45}
- **afiliacions_rg_res/cat**: 110 files, 0 valors buits (0.0%) | períodes 2012M03–2026M09 (110), estats: {'p': 1}
- **afiliacions_rg_res/at**: 1100 files, 0 valors buits (0.0%) | períodes 2012M03–2026M09 (110), estats: {'p': 10}
- **afiliacions_rg_res/com**: 4950 files, 82 valors buits (1.7%) | períodes 2012M03–2026M09 (110), estats: {'..': 82, 'p': 45}
- **afiliacions_rg_lloc/cat**: 105 files, 0 valors buits (0.0%) | períodes 2020M12–2025M12 (21), estats: {'p': 105}
- **afiliacions_rg_lloc/at**: 1050 files, 0 valors buits (0.0%) | períodes 2020M12–2025M12 (21), estats: {'p': 1050}
- **afiliacions_rg_lloc/com**: 4725 files, 50 valors buits (1.1%) | períodes 2020M12–2025M12 (21), estats: {'p': 4675, '..': 50}
- **poblacio_16_64/at**: 801 files, 11 valors buits (1.4%) | períodes 1981S1–2025S1 (89), estats: {'..': 11}
- **poblacio_16_64/com**: 3916 files, 154 valors buits (3.9%) | períodes 1981S1–2025S1 (89), estats: {'..': 154}
- **taxes_mercat_cat/cat**: 783 files, 0 valors buits (0.0%) | períodes 2005M01–2026M09 (261), estats: {'p': 36, 'a': 9}
- **poblacio_mun/mun**: 936 files, 828 valors buits (88.5%) | períodes 1986S2–2025S1 (78), estats: {'..': 828}
- **afiliats_res_mun/mun**: 1320 files, 0 valors buits (0.0%) | períodes 2012M03–2026M09 (110), estats: {'p': 12}

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
- ⚠️ afiliats_res: 107 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code       source period_code   SEX               CONCEPT    value  value_at  rel_diff
      AT06 afiliats_res     2014M06 TOTAL CONTRIB_SP_SOCIAL_SEC 146282.0  148265.0  0.013375
      AT06 afiliats_res     2014M03 TOTAL CONTRIB_SP_SOCIAL_SEC 143710.0  145653.0  0.013340
      AT06 afiliats_res     2014M09 TOTAL CONTRIB_SP_SOCIAL_SEC 145904.0  147850.0  0.013162
      AT06 afiliats_res     2015M03 TOTAL CONTRIB_SP_SOCIAL_SEC 149097.0  151065.0  0.013028
      AT06 afiliats_res     2014M12 TOTAL CONTRIB_SP_SOCIAL_SEC 147026.0  148963.0  0.013003
- ⚠️ afiliacions_rg_res: 107 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code             source period_code            CON_REG_SS             CONCEPT    value  value_at  rel_diff
      AT06 afiliacions_rg_res     2014M06 REG_GRL_SP_COALMINING AFFILIAT_SP_SOC_SEC 116329.0  117816.0  0.012621
      AT06 afiliacions_rg_res     2014M03 REG_GRL_SP_COALMINING AFFILIAT_SP_SOC_SEC 114405.0  115866.0  0.012609
      AT06 afiliacions_rg_res     2014M09 REG_GRL_SP_COALMINING AFFILIAT_SP_SOC_SEC 116129.0  117601.0  0.012517
      AT06 afiliacions_rg_res     2014M12 REG_GRL_SP_COALMINING AFFILIAT_SP_SOC_SEC 117313.0  118795.0  0.012475
      AT06 afiliacions_rg_res     2015M03 REG_GRL_SP_COALMINING AFFILIAT_SP_SOC_SEC 119447.0  120953.0  0.012451
- ⚠️ poblacio_16_64: 257 combinacions superen la tolerància (0.5%). Pitjors:
ambit_code         source period_code   SEX      AGE CONCEPT    value  value_at  rel_diff
      AT08 poblacio_16_64      2010S1 TOTAL Y016_064     POP 312452.0   51165.0  5.106753
      AT08 poblacio_16_64      2009S2 TOTAL Y016_064     POP 311939.0   51223.0  5.089823
      AT08 poblacio_16_64      2010S2 TOTAL Y016_064     POP 312770.0   51421.0  5.082534
      AT08 poblacio_16_64      2009S1 TOTAL Y016_064     POP 311435.0   51289.0  5.072160
      AT08 poblacio_16_64      2011S1 TOTAL Y016_064     POP 313085.0   51687.0  5.057326
