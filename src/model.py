"""Genera un model en estrella (CSV) per a Power BI a partir de data/processed/.

Ús (després de `python src/extract.py`):
    python src/model.py

Sortida a data/model/:
    dim_territori.csv   una fila per comarca, amb l'àmbit com a atribut (jerarquia Àmbit > Comarca)
    dim_indicador.csv   indicadors: nom, unitat, si es poden sumar i com s'agreguen
    dim_sector.csv      sectors del VAB
    dim_any.csv         anys
    fact_indicadors.csv gra: comarca × any × indicador
    fact_vab.csv        gra: comarca × any × sector
    ref_oficial.csv     valors oficials d'àmbit i Catalunya (per conciliar amb la suma de comarques)

Decisió de disseny: els fets són a nivell de comarca i els àmbits s'obtenen sumant
comarques (vegeu README, "Notes metodològiques"). Els indicadors no additius
(renda, IST...) s'agreguen amb mitjana ponderada per població a les mesures DAX.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODEL = ROOT / "data" / "model"

# codi -> (font, nom, unitat, agregació)
INDICADORS = {
    "GDP_ME":          ("pib", "PIB", "milions €", "suma"),
    "GDP_E_INH":       ("pib", "PIB per habitant (oficial)", "€", "no agregable"),
    "POP":             ("poblacio", "Població (1 de gener)", "persones", "suma"),
    "IST_G_IND":       ("ist", "Índex socioeconòmic territorial", "índex Catalunya=100", "mitjana ponderada per població"),
    "AVER_INC_EUR":    ("ist_indicadors", "Renda mitjana per persona", "€", "mitjana ponderada per població"),
    "POP_EMP_PERC":    ("ist_indicadors", "Població ocupada", "%", "mitjana ponderada per població"),
    "WOR_LOWSK _PERC": ("ist_indicadors", "Treballadors de baixa qualificació", "%", "mitjana ponderada per població"),
    "POP_PS_EDU_PERC": ("ist_indicadors", "Població amb estudis baixos", "%", "mitjana ponderada per població"),
    "POP_Y_WSTU_PERC": ("ist_indicadors", "Població jove sense estudis postobligatoris", "%", "mitjana ponderada per població"),
    "POP_INC_LM_PERC": ("ist_indicadors", "Població estrangera de països de renda baixa o mitjana", "%", "mitjana ponderada per població"),
}


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{name}.csv", dtype={"geo_code": str, "period_code": str})


def to_year(df: pd.DataFrame) -> pd.DataFrame:
    """Anys enters. Per a la població (semestral) ens quedem amb S1 = 1 de gener."""
    df = df[~df["period_code"].str.endswith("S2")].copy()
    df["any"] = df["period_code"].str[:4].astype(int)
    return df


def main() -> None:
    MODEL.mkdir(parents=True, exist_ok=True)
    ambits = pd.read_csv(ROOT / "config" / "ambits_comarques.csv")

    # ---- Dimensió territori (comarques) ---------------------------------------
    pob = load("poblacio_com")
    com = (pob.loc[pob["geo_code"] != "TOTAL", ["geo_code", "geo_label"]].drop_duplicates()
           .rename(columns={"geo_code": "comarca_code", "geo_label": "comarca"}))
    dim_territori = com.merge(ambits, on="comarca", how="left").sort_values(["ambit_code", "comarca"])
    assert dim_territori["ambit_code"].notna().all(), "Hi ha comarques sense àmbit a config/"
    # Ordre dels àmbits pel PIB de l'últim any (com a la infografia Python). A Power BI,
    # "Ordena per columna" ambit -> ambit_ordre fa que els colors del tema segueixin aquest ordre.
    pib = load("pib_com")
    pib = pib[(pib["CONCEPT"] == "GDP_ME") & (pib["geo_code"] != "TOTAL")]
    pib = pib[pib["period_code"] == pib["period_code"].max()].merge(ambits, left_on="geo_label", right_on="comarca")
    ordre = pib.groupby("ambit")["value"].sum().sort_values(ascending=False)
    dim_territori["ambit_ordre"] = dim_territori["ambit"].map({a: i for i, a in enumerate(ordre.index, 1)})
    dim_territori.to_csv(MODEL / "dim_territori.csv", index=False)

    # ---- Fets: indicadors per comarca ------------------------------------------
    parts = []
    for code, (src, *_rest) in INDICADORS.items():
        d = load(f"{src}_com")
        d = d[(d["CONCEPT"] == code) & (d["geo_code"] != "TOTAL")]
        parts.append(to_year(d))
    fact = pd.concat(parts)
    fact = (fact.rename(columns={"geo_code": "comarca_code", "CONCEPT": "indicador_code",
                                 "value": "valor", "status": "estat"})
            [["comarca_code", "any", "indicador_code", "valor", "estat"]]
            .dropna(subset=["valor"]))
    fact.to_csv(MODEL / "fact_indicadors.csv", index=False)

    # ---- Fets: VAB per sector --------------------------------------------------
    vab = to_year(load("vab_com"))
    vab = vab[(vab["geo_code"] != "TOTAL") & (vab["SEC_ACTIV_G"] != "TOTAL")]
    fact_vab = (vab.rename(columns={"geo_code": "comarca_code", "SEC_ACTIV_G": "sector_code",
                                    "value": "vab_meur", "status": "estat"})
                [["comarca_code", "any", "sector_code", "vab_meur", "estat"]]
                .dropna(subset=["vab_meur"]))
    fact_vab.to_csv(MODEL / "fact_vab.csv", index=False)

    # ---- Dimensions petites ----------------------------------------------------
    pd.DataFrame([{"indicador_code": k, "indicador": v[1], "unitat": v[2], "agregacio": v[3], "font_idescat": v[0]}
                  for k, v in INDICADORS.items()]).to_csv(MODEL / "dim_indicador.csv", index=False)

    (vab[["SEC_ACTIV_G", "SEC_ACTIV_G_label"]].drop_duplicates()
     .rename(columns={"SEC_ACTIV_G": "sector_code", "SEC_ACTIV_G_label": "sector"})
     .assign(ordre=lambda d: range(1, len(d) + 1))
     .to_csv(MODEL / "dim_sector.csv", index=False))

    # ---- Referència oficial (àmbits i Catalunya) per conciliar ------------------
    ref = []
    for src, concepts in (("pib", ["GDP_ME", "GDP_E_INH"]), ("poblacio", ["POP"])):
        for geo, nivell in (("at", "Àmbit"), ("cat", "Catalunya")):
            d = to_year(load(f"{src}_{geo}"))
            d = d[d["CONCEPT"].isin(concepts)]
            if geo == "cat":
                d = d.assign(geo_code="CAT", geo_label="Catalunya")
            ref.append(d.loc[d["geo_code"] != "TOTAL"].assign(nivell=nivell))
    (pd.concat(ref).rename(columns={"geo_code": "codi", "geo_label": "nom", "CONCEPT": "indicador_code",
                                    "value": "valor_oficial"})
     [["nivell", "codi", "nom", "any", "indicador_code", "valor_oficial"]]
     .to_csv(MODEL / "ref_oficial.csv", index=False))

    ref_anys = pd.read_csv(MODEL / "ref_oficial.csv")["any"]
    anys = range(min(fact["any"].min(), ref_anys.min()), max(fact["any"].max(), ref_anys.max()) + 1)
    pd.DataFrame({"any": list(anys)}).to_csv(MODEL / "dim_any.csv", index=False)

    for f in sorted(MODEL.glob("*.csv")):
        print(f"{f.name:22} {sum(1 for _ in f.open(encoding='utf-8')) - 1:>6} files")


if __name__ == "__main__":
    main()
