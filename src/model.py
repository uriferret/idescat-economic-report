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
    fact_afiliacions_sector.csv  gra: comarca × any × sector (afiliacions al règim general per lloc de treball)
    fact_mercat_cat.csv gra: mes (Catalunya): taxes d'activitat, ocupació i atur
    ref_oficial.csv     valors oficials d'àmbit i Catalunya (per conciliar amb la suma de comarques)
    fact_ambit_oficial.csv  població i afiliats oficials per àmbit (gra: àmbit × any × indicador)

Decisió de disseny: els fets són a nivell de comarca i els àmbits s'obtenen sumant
comarques (vegeu README, "Notes metodològiques"). El PIB per habitant es calcula amb la
població a 1 de juliol (POP_JUL), com fa l'Idescat.

Excepció: 12 municipis pertanyen a un àmbit diferent del de la seva comarca
(config/municipis_ambit_diferent.csv). Per a la població i els afiliats, les mesures DAX
d'àmbit fan servir les xifres oficials per àmbit (fact_ambit_oficial), que ja assignen
cada municipi al seu àmbit. El PIB i el VAB es mantenen com a suma de comarques, perquè
l'Idescat no publica el PIB dels municipis de menys de 5.000 habitants. Els indicadors no additius
(renda, IST...) s'agreguen amb mitjana ponderada per població a les mesures DAX.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODEL = ROOT / "data" / "model"

# codi -> (font, nom, unitat, agregació[, concepte de l'API, filtres addicionals])
# Si no s'indica el concepte, és el mateix codi.
INDICADORS = {
    "GDP_ME":          ("pib", "PIB", "milions €", "suma"),
    "GDP_E_INH":       ("pib", "PIB per habitant (oficial)", "€", "no agregable"),
    "POP":             ("poblacio", "Població (1 de gener)", "persones", "suma"),
    # Població a 1 de juliol: és la que fa servir l'Idescat per al PIB per habitant.
    "POP_JUL":         ("poblacio", "Població (1 de juliol)", "persones", "suma", "POP", {"_semestre": "S2"}),
    "IST_G_IND":       ("ist", "Índex socioeconòmic territorial", "índex Catalunya=100", "mitjana ponderada per població"),
    "AVER_INC_EUR":    ("ist_indicadors", "Renda mitjana per persona", "€", "mitjana ponderada per població"),
    "POP_EMP_PERC":    ("ist_indicadors", "Població ocupada", "%", "mitjana ponderada per població"),
    "WOR_LOWSK _PERC": ("ist_indicadors", "Treballadors de baixa qualificació", "%", "mitjana ponderada per població"),
    "POP_PS_EDU_PERC": ("ist_indicadors", "Població amb estudis baixos", "%", "mitjana ponderada per població"),
    "POP_Y_WSTU_PERC": ("ist_indicadors", "Població jove sense estudis postobligatoris", "%", "mitjana ponderada per població"),
    "POP_INC_LM_PERC": ("ist_indicadors", "Població estrangera de països de renda baixa o mitjana", "%", "mitjana ponderada per població"),
    # Mercat laboral (dades a 31 de desembre)
    "AFI_RES":     ("afiliats_res", "Afiliats a la Seguretat Social residents a la comarca", "persones", "suma",
                    "CONTRIB_SP_SOCIAL_SEC"),
    "AFI_RG_RES":  ("afiliacions_rg_res", "Afiliacions al règim general de residents a la comarca", "afiliacions", "suma",
                    "AFFILIAT_SP_SOC_SEC"),
    "AFI_RG_LLOC": ("afiliacions_rg_lloc", "Afiliacions al règim general en centres de treball de la comarca", "afiliacions", "suma",
                    "AFFIL_SS_GENRL_CL_REGIME", {"SEC_ACTIV_G": "TOTAL"}),
    "POP_16_64":   ("poblacio_16_64", "Població de 16 a 64 anys (1 de gener)", "persones", "suma", "POP"),
}


# Indicadors amb xifres oficials per àmbit, i primer any en què l'Idescat assigna els
# municipis de config/municipis_ambit_diferent.csv al seu àmbit (abans, Alta Segarra al Penedès).
AMBIT_OFICIAL = {"POP": 2015, "POP_JUL": 2015, "POP_16_64": 2015,
                 "AFI_RES": 2015, "AFI_RG_RES": 2015, "AFI_RG_LLOC": 2015}


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{name}.csv", dtype={"geo_code": str, "period_code": str})


def to_year(df: pd.DataFrame) -> pd.DataFrame:
    """Anys enters. Semestres: S1 (1 de gener). Mesos: desembre (31 de desembre)."""
    p = df["period_code"].astype(str)
    keep = ~p.str.endswith("S2") & (~p.str.contains("M") | p.str.endswith("M12"))
    df = df[keep].copy()
    df["any"] = df["period_code"].astype(str).str[:4].astype(int)
    return df


def to_year_s2(df: pd.DataFrame) -> pd.DataFrame:
    """Només el segon semestre (1 de juliol), amb l'any com a enter."""
    df = df[df["period_code"].astype(str).str.endswith("S2")].copy()
    df["any"] = df["period_code"].astype(str).str[:4].astype(int)
    return df


def main() -> None:
    MODEL.mkdir(parents=True, exist_ok=True)
    ambits = pd.read_csv(ROOT / "config" / "ambits_comarques.csv")
    canvis = pd.read_csv(ROOT / "config" / "canvis_limits_comarcals.csv")

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
    # Comarques amb límits modificats: les seves sèries llargues (1981, 2012) no són comparables.
    nota = canvis.groupby("comarca")["descripcio"].agg(" ".join)
    dim_territori["canvi_limits"] = dim_territori["comarca"].map(nota).fillna("")
    dim_territori["serie_comparable"] = dim_territori["canvi_limits"].eq("")
    dim_territori.to_csv(MODEL / "dim_territori.csv", index=False)

    # ---- Fets: indicadors per comarca ------------------------------------------
    comarques = set(dim_territori["comarca_code"])  # exclou "99: no residents a Catalunya"
    parts = []
    for code, (src, _nom, _unitat, _agr, *extra) in INDICADORS.items():
        concept = extra[0] if extra else code
        filtres = dict(extra[1]) if len(extra) > 1 else {}
        semestre = filtres.pop("_semestre", None)
        d = load(f"{src}_com")
        d = d[(d["CONCEPT"] == concept) & d["geo_code"].isin(comarques)]
        for col, val in filtres.items():
            d = d[d[col] == val]
        d = to_year_s2(d) if semestre == "S2" else to_year(d)
        parts.append(d.assign(CONCEPT=code))
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

    # ---- Fets: afiliacions per lloc de treball i sector ------------------------
    afs = to_year(load("afiliacions_rg_lloc_com"))
    afs = afs[afs["geo_code"].isin(comarques) & (afs["SEC_ACTIV_G"] != "TOTAL")]
    (afs.rename(columns={"geo_code": "comarca_code", "SEC_ACTIV_G": "sector_code",
                         "value": "afiliacions", "status": "estat"})
     [["comarca_code", "any", "sector_code", "afiliacions", "estat"]]
     .dropna(subset=["afiliacions"])
     .to_csv(MODEL / "fact_afiliacions_sector.csv", index=False))

    # ---- Fets: taxes mensuals del mercat de treball (Catalunya) ----------------
    mc = load("taxes_mercat_cat_cat")
    mc = mc[mc["INDICATOR"] == "VALUE_PERC"].copy()
    mc["any"] = mc["period_code"].str[:4].astype(int)
    mc["mes"] = mc["period_code"].str[5:].astype(int)
    mc["data"] = pd.to_datetime(dict(year=mc["any"], month=mc["mes"], day=1)).dt.strftime("%Y-%m-%d")
    (mc.rename(columns={"CONCEPT": "indicador_code", "CONCEPT_label": "indicador", "value": "valor", "status": "estat"})
     [["data", "any", "mes", "indicador_code", "indicador", "valor", "estat"]]
     .to_csv(MODEL / "fact_mercat_cat.csv", index=False))

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

    # ---- Població i afiliats oficials per àmbit ----------------------------------
    amb = []
    for code, inici in AMBIT_OFICIAL.items():
        src, _nom, _unitat, _agr, *extra = INDICADORS[code]
        concept = extra[0] if extra else code
        filtres = dict(extra[1]) if len(extra) > 1 else {}
        semestre = filtres.pop("_semestre", None)
        if not (PROCESSED / f"{src}_at.csv").exists():
            print(f"Avís: falta data/processed/{src}_at.csv; executa python src/extract.py")
            continue
        d = load(f"{src}_at")
        d = d[(d["CONCEPT"] == concept) & d["geo_code"].isin(ambits["ambit_code"])]
        for col, val in filtres.items():
            d = d[d[col] == val]
        d = to_year_s2(d) if semestre == "S2" else to_year(d)
        amb.append(d[d["any"] >= inici].assign(indicador_code=code))
    cols = ["ambit_code", "any", "indicador_code", "valor"]
    (pd.concat(amb).rename(columns={"geo_code": "ambit_code", "value": "valor"})[cols].dropna(subset=["valor"])
     if amb else pd.DataFrame(columns=cols)).to_csv(MODEL / "fact_ambit_oficial.csv", index=False)

    ref_anys = pd.read_csv(MODEL / "ref_oficial.csv")["any"]
    anys = range(min(fact["any"].min(), ref_anys.min()), max(fact["any"].max(), ref_anys.max()) + 1)
    pd.DataFrame({"any": list(anys)}).to_csv(MODEL / "dim_any.csv", index=False)

    for f in sorted(MODEL.glob("*.csv")):
        print(f"{f.name:22} {sum(1 for _ in f.open(encoding='utf-8')) - 1:>6} files")


if __name__ == "__main__":
    main()
