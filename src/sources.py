"""Catàleg de taules de l'Idescat que fa servir el projecte.

Per afegir un indicador nou només cal afegir una entrada aquí.
Les rutes s'han comprovat al catàleg https://api.idescat.cat/taules/v2
"""

SOURCES = {
    # PIB (milions €), PIB per habitant (€) i índex Catalunya=100. 2011-2023.
    "pib": {
        "stat": "pibc", "node": 21925, "table": 26069,
        "geos": ["cat", "at", "com"],
        "description": "PIB i PIB per habitant. Revisió estadística 2024",
    },
    # VAB (milions €) per sectors: A agricultura, B-E indústria, F construcció, G-U serveis.
    "vab": {
        "stat": "pibc", "node": 21926, "table": 26070,
        "geos": ["cat", "at", "com"],
        "description": "Valor afegit brut per sectors d'activitat. Revisió estadística 2024",
    },
    # Població per semestres des de 1981. Filtrem el total per no superar el límit de cel·les.
    "poblacio": {
        "stat": "ep", "node": 9122, "table": 10002,
        "geos": ["cat", "at", "com"],
        "filters": {"SEX": "TOTAL"},
        "description": "Estimacions de població. Total",
    },
    # Índex socioeconòmic territorial (Catalunya=100). Equivalent català de l'HDI.
    "ist": {
        "stat": "ist", "node": 14034, "table": 14994,
        "geos": ["cat", "com"],
        "description": "Índex socioeconòmic territorial (IST). Índex Catalunya=100",
    },
    # Components de l'IST en valors (inclou renda mitjana per persona).
    "ist_indicadors": {
        "stat": "ist", "node": 14074, "table": 15022,
        "geos": ["com"],
        "description": "Indicadors socioeconòmics. Valors",
    },
    # ---- Mercat laboral -------------------------------------------------------
    # Afiliats (persones) per comarca de residència. Mensual des de 2020 (trimestral abans).
    "afiliats_res": {
        "stat": "afi", "node": 8604, "table": 8704,
        "geos": ["cat", "com"],
        "filters": {"SEX": "TOTAL"},
        "description": "Afiliats a la Seguretat Social segons residència. A últim dia del mes",
    },
    # Afiliacions al règim general per comarca de residència (per comparar amb el lloc de treball).
    "afiliacions_rg_res": {
        "stat": "afi", "node": 8603, "table": 8703,
        "geos": ["cat", "com"],
        "filters": {"CON_REG_SS": "REG_GRL_SP_COALMINING"},
        "description": "Afiliacions al règim general segons residència. A últim dia del mes",
    },
    # Afiliacions al règim general per comarca del centre de treball, per sectors (CCAE-2009, 12/2020-12/2025).
    "afiliacions_rg_lloc": {
        "stat": "afic", "node": 14983, "table": 15879,
        "geos": ["cat", "com"],
        "description": "Afiliacions al règim general per sector d'activitat (lloc de treball). A últim dia del mes",
    },
    # Població de 16 a 64 anys (denominador de la taxa d'afiliació).
    "poblacio_16_64": {
        "stat": "ep", "node": 17363, "table": 20891,
        "geos": ["com"],
        "filters": {"SEX": "TOTAL", "AGE": "Y016_064"},
        "description": "Estimacions de població de 16 a 64 anys",
    },
    # Taxes mensuals d'activitat, ocupació i atur (només Catalunya).
    "taxes_mercat_cat": {
        "stat": "e03", "node": 22274, "table": 26671,
        "geos": ["cat"],
        "filters": {"INDICATOR": "VALUE_PERC"},
        "description": "Estimació mensual de la població activa. Taxes d'activitat, ocupació i atur",
    },
}

# Conceptes que es poden sumar de comarques a àmbits (per al control de qualitat).
ADDITIVE_CONCEPTS = {
    "pib": ["GDP_ME"],
    "vab": ["GVA_M_EUR"],
    "poblacio": ["POP"],
}
