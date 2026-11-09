"""Valida les dades descarregades i el model de Power BI.

Ús (després de `python src/extract.py` i `python src/model.py`):
    python src/validate.py

Escriu data/processed/validacio.md i acaba amb codi 1 si alguna comprovació falla.
"""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
MODEL = ROOT / "data" / "model"
CONFIG = ROOT / "config"

TOL_TOTAL = 0.001    # suma de comarques vs Catalunya (arrodoniments)
TOL_PIB_HAB = 0.005  # PIB per habitant calculat vs oficial (últim any)
TOL_MUNICIPIS = 0.02  # diferència d'àmbit explicada pels municipis reassignats
ARRODONIMENT = 25     # els afiliats es publiquen arrodonits a múltiples de 5 per territori
TOL_RENDA_MUN = 0.005  # renda dels municipis ponderada per població vs Catalunya
TOL_ATUR_EMEX = 0.005  # atur dels municipis (sense els «<5») vs Catalunya a l'EMEX
MUNICIPIS = 947

resultats: list[tuple[bool, str]] = []
detall: list[str] = []


def ok(condicio: bool, text: str) -> None:
    resultats.append((bool(condicio), text))


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{name}.csv", dtype={"geo_code": str, "period_code": str})


def comarques(df: pd.DataFrame) -> pd.DataFrame:
    """Només comarques: treu el total de Catalunya i el codi 99 (no residents a Catalunya o altres)."""
    return df[df["geo_code"].str.fullmatch(r"\d\d") & (df["geo_code"] != "99")]


def taula(df: pd.DataFrame) -> str:
    return "```\n" + df.to_string(index=False) + "\n```"


# ---- 1. Suma de comarques = Catalunya ---------------------------------------
def suma_comarques_catalunya() -> None:
    casos = [("pib", "GDP_ME", []), ("vab", "GVA_M_EUR", ["SEC_ACTIV_G"]), ("poblacio", "POP", []),
             ("afiliats_res", "CONTRIB_SP_SOCIAL_SEC", [])]
    for src, concept, keys in casos:
        com, cat = load(f"{src}_com"), load(f"{src}_cat")
        sense = com[(com["geo_code"] == "99") & (com["CONCEPT"] == concept)]
        com = comarques(com)
        com, cat = com[com["CONCEPT"] == concept], cat[cat["CONCEPT"] == concept]
        g = com.groupby(["period_code", *keys])["value"].sum().rename("comarques").reset_index()
        g = g.merge(cat[["period_code", *keys, "value"]], on=["period_code", *keys])
        if len(sense):  # codi 99: afiliats no residents a Catalunya o sense residència coneguda
            g = g.merge(sense.groupby(["period_code", *keys])["value"].sum().rename("sense_assignar").reset_index(),
                        on=["period_code", *keys], how="left").fillna({"sense_assignar": 0})
            g["comarques"] += g["sense_assignar"]
        rel = (g["comarques"] / g["value"] - 1).abs().max()
        nota = " (comptant els afiliats no residents a Catalunya o sense residència coneguda)" if len(sense) else ""
        ok(rel <= TOL_TOTAL, f"{src}: suma de comarques = Catalunya{nota}. Diferència màxima {rel:.3%}")


# ---- 2. PIB per habitant del model = oficial ---------------------------------
def pib_per_habitant() -> None:
    f = pd.read_csv(MODEL / "fact_indicadors.csv", dtype={"comarca_code": str})
    d = pd.read_csv(MODEL / "dim_territori.csv", dtype={"comarca_code": str})
    darrer = f.loc[f["indicador_code"] == "GDP_ME", "any"].max()
    p = (f[f["any"] == darrer].merge(d, on="comarca_code")
         .pivot_table(index="comarca", columns="indicador_code", values="valor"))
    p["calculat"] = p["GDP_ME"] * 1e6 / p["POP_JUL"]
    p["dif"] = p["calculat"] / p["GDP_E_INH"] - 1
    pitjor = p["dif"].abs()
    ok(pitjor.max() <= TOL_PIB_HAB,
       f"PIB per habitant {darrer} (PIB / població a 1 de juliol) = oficial a totes les comarques. "
       f"Diferència màxima {pitjor.max():.2%} ({pitjor.idxmax()})")
    ok(p["calculat"].notna().sum() == p["GDP_E_INH"].notna().sum(),
       f"PIB per habitant {darrer}: totes les comarques amb valor oficial tenen valor calculat")
    ref = pd.read_csv(MODEL / "ref_oficial.csv")
    cat = ref.query("nivell == 'Catalunya' and indicador_code == 'GDP_E_INH' and any == @darrer")["valor_oficial"].item()
    calc = p["GDP_ME"].sum() * 1e6 / p["POP_JUL"].sum()
    ok(abs(calc / cat - 1) <= TOL_PIB_HAB, f"PIB per habitant de Catalunya {darrer}: {calc:,.0f} € (oficial {cat:,.0f} €)")


# ---- 3. Àmbits: oficial vs suma de comarques, explicat pels municipis ----------
def ambits() -> None:
    mapa = pd.read_csv(CONFIG / "ambits_comarques.csv")
    muns = pd.read_csv(CONFIG / "municipis_ambit_diferent.csv", dtype={"codi": str})
    muns["ambit_comarca"] = muns["comarca"].map(mapa.set_index("comarca")["ambit_code"])
    casos = [("poblacio", "POP", "poblacio_mun"), ("afiliats_res", "CONTRIB_SP_SOCIAL_SEC", "afiliats_res_mun")]
    for src, concept, src_mun in casos:
        if not (PROCESSED / f"{src}_at.csv").exists() or not (PROCESSED / f"{src_mun}_mun.csv").exists():
            ok(False, f"{src}: falten les dades per àmbit o per municipi (executa python src/extract.py)")
            continue
        com = comarques(load(f"{src}_com")).merge(mapa, left_on="geo_label", right_on="comarca")
        com = com[com["CONCEPT"] == concept]
        at = load(f"{src}_at")
        at = at[(at["CONCEPT"] == concept) & at["geo_code"].isin(mapa["ambit_code"])]
        mun = load(f"{src_mun}_mun")
        mun = mun[mun["CONCEPT"] == concept].merge(muns, left_on="geo_code", right_on="codi")
        darrer = mun.dropna(subset=["value"]).groupby("period_code")["geo_code"].nunique()
        darrer = darrer[darrer == len(muns)].index.max()  # últim període amb tots els municipis
        dif = (at[at["period_code"] == darrer].set_index("geo_code")["value"]
               - com[com["period_code"] == darrer].groupby("ambit_code")["value"].sum())
        m = mun[mun["period_code"] == darrer]
        esperat = (m.groupby("ambit_code")["value"].sum()
                   .sub(m.groupby("ambit_comarca")["value"].sum(), fill_value=0))
        t = pd.DataFrame({"oficial - suma de comarques": dif, "municipis reassignats": esperat}).fillna(0)
        t = t.loc[(t != 0).any(axis=1)]
        t["diferència"] = t.iloc[:, 0] - t.iloc[:, 1]
        marge = (t["municipis reassignats"].abs() * TOL_MUNICIPIS).clip(lower=ARRODONIMENT)
        maxim = t["diferència"].abs().max()
        ok((t["diferència"].abs() <= marge).all(),
           f"{src} {darrer}: la diferència entre l'àmbit oficial i la suma de comarques l'expliquen "
           f"els {len(muns)} municipis de config/municipis_ambit_diferent.csv (desviació màxima {maxim:,.0f})")
        detall.append(f"### {src} · {darrer}\n\n" + taula(t.reset_index(names="àmbit")) + "\n")


# ---- 4. Integritat del model ---------------------------------------------------
def model() -> None:
    d = pd.read_csv(MODEL / "dim_territori.csv", dtype={"comarca_code": str})
    ok(d["comarca_code"].is_unique and len(d) == 43, f"dim_territori: {len(d)} comarques sense duplicats")
    ok(d["ambit_code"].notna().all(), "dim_territori: totes les comarques tenen àmbit")
    for nom, claus in [("fact_indicadors", ["comarca_code", "any", "indicador_code"]),
                       ("fact_vab", ["comarca_code", "any", "sector_code"]),
                       ("fact_afiliacions_sector", ["comarca_code", "any", "sector_code"])]:
        f = pd.read_csv(MODEL / f"{nom}.csv", dtype={"comarca_code": str})
        ok(not f.duplicated(claus).any(), f"{nom}: sense files duplicades")
        orfes = sorted(set(f["comarca_code"]) - set(d["comarca_code"]))
        ok(not orfes, f"{nom}: totes les comarques existeixen a dim_territori" + (f" (orfes: {orfes})" if orfes else ""))
    a = pd.read_csv(MODEL / "fact_ambit_oficial.csv")
    resum = a.groupby("indicador_code")["any"].agg(["min", "max", "count"])
    ok(len(resum) == 6, f"fact_ambit_oficial: {len(resum)} de 6 indicadors amb xifres oficials per àmbit")
    detall.append("### fact_ambit_oficial\n\n" + taula(resum.reset_index()))


# ---- 5. Municipis: atur registrat (SEPE) i renda (Idescat) ---------------------
def municipis() -> None:
    dim = pd.read_csv(MODEL / "dim_municipi.csv", dtype={"municipi_code": str, "codi_idescat": str})
    f = pd.read_csv(MODEL / "fact_municipis.csv", dtype={"municipi_code": str}, keep_default_na=False,
                    na_values=[""])
    ok(len(dim) == MUNICIPIS and dim["municipi_code"].is_unique, f"dim_municipi: {len(dim)} municipis sense duplicats")
    ok(not f.duplicated(["municipi_code", "any", "indicador_code"]).any(), "fact_municipis: sense files duplicades")
    orfes = sorted(set(f["municipi_code"]) - set(dim["municipi_code"]))
    ok(not orfes, "fact_municipis: tots els municipis existeixen a dim_municipi" + (f" (orfes: {orfes[:5]})" if orfes else ""))

    # Atur: cada any, els 947 municipis; i la mitjana anual és la de l'EMEX.
    atur = f[f["indicador_code"] == "ATUR_REG"]
    per_any = atur.groupby("any")["municipi_code"].nunique()
    ok((per_any == MUNICIPIS).all(), f"Atur registrat {per_any.index.min()}-{per_any.index.max()}: "
       f"els {MUNICIPIS} municipis cada any (mínim {per_any.min()})")
    ref = pd.read_csv(PROCESSED / "ref_emex_atur.csv", dtype={"municipi_code": str})
    darrer = int(ref["any"].max())
    a = atur[atur["any"] == darrer]
    suma, cat = a["valor"].sum(), ref["atur_catalunya"].iloc[0]
    amagats = int((a["estat"] == "<5").sum())
    ok(suma <= cat and 1 - suma / cat <= TOL_ATUR_EMEX,
       f"Atur registrat {darrer}: la suma dels municipis ({suma:,.0f}) és la de Catalunya a l'EMEX ({cat:,.0f}), "
       f"menys els {amagats} municipis que el SEPE amaga («<5»): diferència {1 - suma / cat:.2%}")
    m = ref.merge(a, on=["municipi_code", "any"], how="left")
    dif = (m["valor"] - m["atur_municipi"]).abs()
    ok(dif.max() <= 0.05, f"Atur registrat {darrer}: la mitjana anual de {len(m)} municipis és la de l'EMEX "
       f"(diferència màxima {dif.max():.2f})")
    detall.append(f"### Atur registrat {darrer} · SEPE i EMEX\n\n" + taula(m[["municipi_code", "atur_municipi", "valor"]]
                  .rename(columns={"atur_municipi": "EMEX", "valor": "SEPE"})) + "\n")

    # Renda: prou municipis, i la mitjana ponderada per població és la de Catalunya.
    renda = f[f["indicador_code"] == "AVER_INC_EUR"]
    pob = f[f["indicador_code"] == "POP"][["municipi_code", "any", "valor"]].rename(columns={"valor": "pob"})
    r = renda.dropna(subset=["valor"]).merge(pob, on=["municipi_code", "any"])
    cat = load("ist_indicadors_cat")
    cat = cat[cat["CONCEPT"] == "AVER_INC_EUR"].assign(any=lambda d: d["period_code"].astype(int)).set_index("any")["value"]
    files = []
    for any_, g in r.groupby("any"):
        if pd.isna(cat.get(any_)):
            continue
        w = (g["valor"] * g["pob"]).sum() / g["pob"].sum()
        files.append({"any": any_, "municipis": len(g), "ponderada": round(w), "Catalunya": cat[any_],
                      "diferència": w / cat[any_] - 1})
    t = pd.DataFrame(files)
    ok((t["municipis"] >= 900).all(), f"Renda per municipi {t['any'].min()}-{t['any'].max()}: "
       f"almenys 900 municipis cada any (mínim {t['municipis'].min()})")
    ok((t["diferència"].abs() <= TOL_RENDA_MUN).all(),
       f"Renda per municipi: la mitjana dels municipis ponderada per població és la de Catalunya "
       f"(diferència màxima {t['diferència'].abs().max():.2%})")
    detall.append("### Renda per municipi · mitjana ponderada i Catalunya\n\n"
                  + taula(t.assign(diferència=t["diferència"].map("{:+.2%}".format))) + "\n")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for prova in (suma_comarques_catalunya, pib_per_habitant, ambits, model, municipis):
        try:
            prova()
        except Exception as exc:  # una prova que peta no ha d'amagar les altres
            ok(False, f"{prova.__name__}: error {type(exc).__name__}: {exc}")
    errors = sum(not r for r, _ in resultats)
    linies = ["# Validació de les dades", "",
              f"{datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · "
              f"{len(resultats) - errors} correctes, {errors} amb incidències", ""]
    linies += [f"- {'✅' if r else '⚠️'} {t}" for r, t in resultats]
    linies += ["", "## Detall", "", *detall]
    (PROCESSED / "validacio.md").write_text("\n".join(linies) + "\n", encoding="utf-8")
    print("\n".join(linies[:len(resultats) + 4]))
    print(f"\nInforme complet: {(PROCESSED / 'validacio.md').relative_to(ROOT)}")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
