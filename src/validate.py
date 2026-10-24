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

resultats: list[tuple[bool, str]] = []
detall: list[str] = []


def ok(condicio: bool, text: str) -> None:
    resultats.append((bool(condicio), text))


def load(name: str) -> pd.DataFrame:
    return pd.read_csv(PROCESSED / f"{name}.csv", dtype={"geo_code": str, "period_code": str})


def comarques(df: pd.DataFrame) -> pd.DataFrame:
    """Només comarques: treu el total de Catalunya i el codi 99 (sense municipi assignat)."""
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
        if len(sense):  # afiliats sense municipi de residència assignat
            g = g.merge(sense.groupby(["period_code", *keys])["value"].sum().rename("sense_assignar").reset_index(),
                        on=["period_code", *keys], how="left").fillna({"sense_assignar": 0})
            g["comarques"] += g["sense_assignar"]
        rel = (g["comarques"] / g["value"] - 1).abs().max()
        nota = " (comptant els afiliats sense municipi assignat)" if len(sense) else ""
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


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    for prova in (suma_comarques_catalunya, pib_per_habitant, ambits, model):
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
