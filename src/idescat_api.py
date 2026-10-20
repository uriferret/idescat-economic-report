"""Client mínim per a l'API Taules v2 de l'Idescat.

L'API retorna JSON-stat 2.0. Aquest mòdul:
  1. construeix la URL  {estadística}/{node}/{taula}/{geo}/data
  2. desa la resposta crua a data/raw (memòria cau, per no repetir peticions)
  3. converteix el JSON-stat en un DataFrame en format llarg

Documentació: https://www.idescat.cat/dev/api/taules/
Condicions d'ús: cal citar l'Idescat com a font i no alterar les dades.
"""
from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import pandas as pd
import requests

BASE_URL = "https://api.idescat.cat/taules/v2"
GEO_DIMS = {"CAT", "PROV", "AT", "COM", "MUN", "AC", "SEC"}
TIME_DIMS = {"YEAR", "SEMESTER", "QUARTER", "MONTH"}

_session = requests.Session()
_session.headers.update({"User-Agent": "idescat-economic-report (projecte de portfolio)"})


class IdescatAPIError(RuntimeError):
    """Error retornat per l'API (HTTP != 200 o resposta de classe 'error')."""


# ---------------------------------------------------------------------------
# Peticions
# ---------------------------------------------------------------------------
def build_url(stat: str, node: int | str, table: int | str, geo: str, data: bool = True) -> str:
    parts = [BASE_URL, stat, str(node), str(table), geo]
    if data:
        parts.append("data")
    return "/".join(parts)


def _cache_key(stat, node, table, geo, filters, lang) -> str:
    filt = [f"{k}-{v}" for k, v in sorted((filters or {}).items())]
    key = "_".join([stat, str(node), str(table), geo, *filt, lang])
    return key.replace(",", "+").replace("/", "-")


def fetch_json(
    stat: str,
    node: int | str,
    table: int | str,
    geo: str,
    filters: dict | None = None,
    lang: str = "ca",
    cache_dir: str | Path | None = None,
    refresh: bool = False,
    pause: float = 1.0,
) -> dict:
    """Descarrega una taula (amb dades) i la desa a la memòria cau.

    `pause` deixa uns segons entre peticions: l'Idescat demana no fer
    peticions repetides en intervals curts.
    """
    cache_file = None
    if cache_dir is not None:
        cache_file = Path(cache_dir) / f"{_cache_key(stat, node, table, geo, filters, lang)}.json"
        if cache_file.exists() and not refresh:
            return json.loads(cache_file.read_text(encoding="utf-8"))

    url = build_url(stat, node, table, geo)
    params = {"lang": lang, **(filters or {})}
    resp = _session.get(url, params=params, timeout=60)
    if resp.status_code != 200:
        raise IdescatAPIError(f"HTTP {resp.status_code} a {resp.url}\n{resp.text[:500]}")

    payload = resp.json()
    if payload.get("class") == "error":
        raise IdescatAPIError(f"Error de l'API a {resp.url}: {payload}")

    if cache_file is not None:
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        cache_file.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    time.sleep(pause)
    return payload


# ---------------------------------------------------------------------------
# JSON-stat -> DataFrame
# ---------------------------------------------------------------------------
def _categories(dimension: dict) -> tuple[list[str], dict]:
    """Retorna (codis ordenats, {codi: etiqueta}) d'una dimensió JSON-stat."""
    cat = dimension["category"]
    labels = cat.get("label", {}) or {}
    index = cat.get("index")
    if index is None:
        codes = list(labels.keys())
    elif isinstance(index, list):
        codes = list(index)
    else:  # dict {codi: posició}
        codes = sorted(index, key=index.get)
    return codes, labels


def _accessor(obj):
    """Permet llegir 'value' i 'status' tant si són llista, dict (dispers) o un sol valor."""
    if obj is None:
        return lambda i: None
    if isinstance(obj, list):
        return lambda i: obj[i] if i < len(obj) else None
    if isinstance(obj, dict):
        return lambda i: obj.get(str(i))
    return lambda i: obj  # un sol valor aplicat a totes les cel·les


def jsonstat_to_df(dataset: dict) -> pd.DataFrame:
    """Converteix un dataset JSON-stat 2.0 en un DataFrame llarg.

    Una columna amb el codi i una altra amb l'etiqueta per a cada dimensió,
    més `value` i `status`. Les dimensions amb rol geogràfic i temporal es
    renomenen a `geo_*` i `period_*` perquè totes les taules quedin iguals.
    """
    ids = dataset["id"]
    dims = [_categories(dataset["dimension"][d]) for d in ids]
    get_value = _accessor(dataset.get("value"))
    get_status = _accessor(dataset.get("status"))

    rows = []
    # JSON-stat ordena les cel·les en ordre "row-major": l'última dimensió varia més ràpid.
    for i, combo in enumerate(itertools.product(*[codes for codes, _ in dims])):
        row = {}
        for dim_id, (_, labels), code in zip(ids, dims, combo):
            row[dim_id] = code
            row[f"{dim_id}_label"] = labels.get(code, code)
        row["value"] = get_value(i)
        row["status"] = get_status(i)
        rows.append(row)

    df = pd.DataFrame(rows)
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    role = dict(dataset.get("role", {}) or {})
    # Si la resposta no indica rols, els dedueix pel nom de la dimensió.
    role.setdefault("geo", [d for d in ids if d in GEO_DIMS])
    role.setdefault("time", [d for d in ids if d in TIME_DIMS])
    rename = {}
    for prefix, dim_list in (("geo", role.get("geo", [])), ("period", role.get("time", []))):
        if len(dim_list) == 1:
            rename[dim_list[0]] = f"{prefix}_code"
            rename[f"{dim_list[0]}_label"] = f"{prefix}_label"
    df = df.rename(columns=rename)

    df.attrs["label"] = dataset.get("label")
    df.attrs["updated"] = dataset.get("updated")
    return df


def fetch_table(stat, node, table, geo, filters=None, lang="ca", cache_dir=None, refresh=False) -> pd.DataFrame:
    """Drecera: descarrega la taula i la retorna com a DataFrame."""
    payload = fetch_json(stat, node, table, geo, filters, lang, cache_dir, refresh)
    return jsonstat_to_df(payload)
