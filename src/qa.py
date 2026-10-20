"""Controls de qualitat de les dades extretes.

1. Totes les comarques de l'API tenen àmbit assignat al fitxer de configuració.
2. La suma de les comarques de cada àmbit coincideix amb el total d'àmbit que
   publica l'Idescat (valida el mapatge comarca -> àmbit i l'extracció).
3. Resum de valors buits i de codis d'estat (dades provisionals, confidencials...).
"""
from __future__ import annotations

import pandas as pd

TOTAL_CODES = {"TOTAL"}


def _norm(s: pd.Series) -> pd.Series:
    return s.astype(str).str.strip().str.casefold()


def attach_ambit(df_com: pd.DataFrame, mapping: pd.DataFrame) -> pd.DataFrame:
    """Afegeix ambit_code i ambit a una taula comarcal (unió per nom de comarca)."""
    m = mapping.assign(_key=_norm(mapping["comarca"]))[["_key", "ambit_code", "ambit"]]
    out = df_com.assign(_key=_norm(df_com["geo_label"])).merge(m, on="_key", how="left")
    return out.drop(columns="_key")


def check_mapping(df_com: pd.DataFrame, mapping: pd.DataFrame) -> list[str]:
    com = df_com[~df_com["geo_code"].isin(TOTAL_CODES)]
    api = set(_norm(com["geo_label"]).unique())
    cfg = set(_norm(mapping["comarca"]))
    issues = []
    if api - cfg:
        issues.append(f"Comarques de l'API sense àmbit: {sorted(api - cfg)}")
    if cfg - api:
        issues.append(f"Comarques del fitxer que no surten a l'API: {sorted(cfg - api)}")
    return issues


def check_aggregation(
    df_com: pd.DataFrame,
    df_at: pd.DataFrame,
    mapping: pd.DataFrame,
    concepts: list[str],
    tol: float = 0.005,
) -> tuple[list[str], pd.DataFrame]:
    """Compara la suma comarcal per àmbit amb el valor d'àmbit publicat.

    `tol` és la diferència relativa màxima admesa (0,5% per arrodoniments).
    """
    key_cols = [c for c in df_com.columns
                if c not in {"geo_code", "geo_label", "value", "status"} and not c.endswith("_label")]

    com = attach_ambit(df_com[~df_com["geo_code"].isin(TOTAL_CODES)], mapping)
    com = com[com["CONCEPT"].isin(concepts)]
    summed = com.groupby(["ambit_code", *key_cols], as_index=False)["value"].sum(min_count=1)

    at = df_at[~df_at["geo_code"].isin(TOTAL_CODES) & df_at["CONCEPT"].isin(concepts)]
    at = at.rename(columns={"geo_code": "ambit_code", "value": "value_at"})[["ambit_code", *key_cols, "value_at"]]

    cmp = summed.merge(at, on=["ambit_code", *key_cols], how="outer")
    cmp["rel_diff"] = (cmp["value"] - cmp["value_at"]).abs() / cmp["value_at"].abs()
    bad = cmp[cmp["rel_diff"] > tol]

    issues = []
    if len(bad):
        worst = bad.sort_values("rel_diff", ascending=False).head(5)
        issues.append(
            f"{len(bad)} combinacions superen la tolerància ({tol:.1%}). Pitjors:\n"
            + worst.to_string(index=False)
        )
    return issues, cmp


def summarize(df: pd.DataFrame, name: str) -> str:
    n = len(df)
    nulls = int(df["value"].isna().sum())
    status = df["status"].dropna().value_counts().to_dict() if "status" in df else {}
    periods = ""
    if "period_code" in df:
        p = sorted(df["period_code"].astype(str).unique())
        periods = f" | períodes {p[0]}–{p[-1]} ({len(p)})"
    return f"- **{name}**: {n} files, {nulls} valors buits ({nulls / max(n, 1):.1%}){periods}, estats: {status or 'cap'}"
