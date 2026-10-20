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
}

# Conceptes que es poden sumar de comarques a àmbits (per al control de qualitat).
ADDITIVE_CONCEPTS = {
    "pib": ["GDP_ME"],
    "vab": ["GVA_M_EUR"],
    "poblacio": ["POP"],
}
