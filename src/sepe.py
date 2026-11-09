"""Atur registrat per municipi, del Servei Públic d'Ocupació Estatal (SEPE).

L'Idescat no en té una taula a l'API de Taules (a l'EMEX només hi ha l'últim
any), i Dades Obertes de la Generalitat no el publica. El SEPE sí: un CSV per
any amb l'atur registrat de cada mes i de cada municipi d'Espanya, des del
2006 (catàleg «Paro registrado por municipio» de datos.gob.es).

Aquest mòdul:
  1. baixa el fitxer de cada any i el desa a data/raw/sepe/ (memòria cau);
  2. es queda amb Catalunya (comunitat autònoma 9) i amb el total de cada
     municipi i mes;
  3. en fa la mitjana anual, que és la xifra anual habitual de l'atur
     registrat (la de l'EMEX de l'Idescat i del Departament d'Empresa i Treball).

Coses de la font, comprovades el 09/11/2026:
  - el fitxer és en ISO-8859-1, amb punt i coma, i una primera línia de títol;
  - el codi de municipi té 4 o 5 xifres segons l'any (8001 o 08001): es
    normalitza al codi INE de 5 xifres;
  - des del 2022, el SEPE amaga els valors per sota de 5 («<5») per secret
    estadístic. Un municipi amb algun mes «<5» no té mitjana anual: no
    s'inventa cap xifra, es marca amb l'estat «<5»;
  - el fitxer del 2020 no porta el desembre: la mitjana del 2020 és de 11
    mesos, i es marca amb l'estat «11m»;
  - el fitxer del 2013 només porta de gener a abril: amb menys de 11 mesos no
    es dona mitjana anual (estat «4m»), perquè no representaria l'any.
"""
from __future__ import annotations

import io
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://sede.sepe.gob.es/es/portaltrabaja/resources/sede/datos_abiertos/datos"
CATALUNYA = "9"
MENYS_DE_5 = "<5"
#: Amb menys mesos, la mitjana no representa l'any i no es dona.
MESOS_MINIMS = 11

_session = requests.Session()
_session.headers.update({"User-Agent": "idescat-economic-report (projecte de portfolio)"})


def url(any_: int) -> str:
    return f"{BASE_URL}/Paro_por_municipios_{any_}_csv.csv"


def fetch_any(any_: int, cache_dir: str | Path | None = None, refresh: bool = False, pause: float = 1.0) -> bytes:
    """El CSV d'un any, de la memòria cau o del SEPE."""
    fitxer = Path(cache_dir) / f"Paro_por_municipios_{any_}.csv" if cache_dir else None
    if fitxer is not None and fitxer.exists() and not refresh:
        return fitxer.read_bytes()
    resp = _session.get(url(any_), timeout=180)
    resp.raise_for_status()
    if "csv" not in resp.headers.get("content-type", ""):
        raise RuntimeError(f"SEPE {any_}: la resposta no és un CSV ({resp.headers.get('content-type')})")
    if fitxer is not None:
        fitxer.parent.mkdir(parents=True, exist_ok=True)
        fitxer.write_bytes(resp.content)
    time.sleep(pause)
    return resp.content


def llegeix(contingut: bytes) -> pd.DataFrame:
    """Els municipis de Catalunya, un per fila i mes: codi INE, nom, mes i total.

    `total` és buit quan la font hi posa «<5»; `menys_de_5` ho diu."""
    df = pd.read_csv(io.BytesIO(contingut), sep=";", skiprows=1, encoding="latin1", dtype=str)
    df.columns = [c.strip() for c in df.columns]
    df = df[df["Código de CA"].str.strip() == CATALUNYA]
    total = df["total Paro Registrado"].str.strip()
    sortida = pd.DataFrame({
        "municipi_code": df["Codigo Municipio"].str.strip().str.zfill(5),
        "municipi": df["Municipio"].str.strip(),
        "mes": df["Código mes"].str.strip(),
        "total": pd.to_numeric(total.where(total != MENYS_DE_5), errors="raise"),
        "menys_de_5": total == MENYS_DE_5,
    })
    if not sortida["mes"].str.fullmatch(r"\d{6}").all():
        raise ValueError("SEPE: hi ha mesos que no tenen la forma AAAAMM")
    return sortida.reset_index(drop=True)


def mitjana_anual(mensual: pd.DataFrame) -> pd.DataFrame:
    """Mitjana anual de cada municipi: codi, nom, any, valor, mesos i estat.

    - amb algun mes «<5», sense valor i estat «<5»;
    - si a la font li falta un mes (el 2020, el desembre), la mitjana dels que
      hi ha i estat «11m»;
    - si en falten més (el 2013 només té de gener a abril), sense valor i estat
      «<n>m» (p. ex. «4m»).

    L'any en curs no s'hi ha de passar: `extreu` només demana anys acabats."""
    m = mensual.assign(any=mensual["mes"].str[:4].astype(int))
    g = m.groupby(["municipi_code", "any"])
    anual = g.agg(
        municipi=("municipi", "last"),
        valor=("total", "mean"),
        mesos=("mes", "nunique"),
        menys_de_5=("menys_de_5", "any"),
    ).reset_index()
    anual.loc[anual["menys_de_5"] | (anual["mesos"] < MESOS_MINIMS), "valor"] = float("nan")
    anual["estat"] = ""
    anual.loc[anual["mesos"] < 12, "estat"] = anual["mesos"].astype(str) + "m"
    anual.loc[anual["menys_de_5"], "estat"] = MENYS_DE_5
    anual["valor"] = anual["valor"].round(1)
    return anual[["municipi_code", "municipi", "any", "valor", "mesos", "estat"]]


def extreu(anys: range, cache_dir: str | Path | None = None, refresh: bool = False) -> pd.DataFrame:
    """La mitjana anual de tots els anys demanats (només anys acabats)."""
    parts = [mitjana_anual(llegeix(fetch_any(a, cache_dir, refresh))) for a in anys]
    return pd.concat(parts, ignore_index=True)


# ---- Referència: l'EMEX de l'Idescat ------------------------------------------
# L'EMEX publica la mitjana anual de l'atur registrat del darrer any (font:
# Departament d'Empresa i Treball) per al municipi, la seva comarca i Catalunya.
# Serveix per comprovar que la mitjana calculada aquí és la mateixa.
EMEX_URL = "https://api.idescat.cat/emex/v1/dades.json"
EMEX_ATUR = "f242"  # Atur registrat. Total (mitjanes anuals)


def referencia_emex(codis_idescat: list[str]) -> pd.DataFrame:
    """Atur registrat de l'EMEX: municipi, any, valor del municipi i de Catalunya."""
    files = []
    for codi in codis_idescat:
        resp = _session.get(EMEX_URL, params={"id": codi, "i": EMEX_ATUR, "lang": "ca"}, timeout=60)
        resp.raise_for_status()
        ind = resp.json()["fitxes"]["indicadors"]["i"]
        ind = ind[0] if isinstance(ind, list) else ind
        mun, _com, cat = (float(v) for v in ind["v"].split(","))
        files.append({"municipi_code": codi[:5], "any": int(ind["r"]), "atur_municipi": mun, "atur_catalunya": cat})
        time.sleep(1.0)
    return pd.DataFrame(files)
