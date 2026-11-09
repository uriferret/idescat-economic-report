"""Extreu totes les taules de sources.py i l'atur registrat del SEPE, les desa en CSV i passa els controls de qualitat.

Ús (des de l'arrel del repositori):
    python src/extract.py            # fa servir la memòria cau de data/raw si existeix
    python src/extract.py --refresh  # torna a descarregar-ho tot
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

import sepe
from idescat_api import IdescatAPIError, build_url, fetch_json, jsonstat_to_df
from qa import check_aggregation, check_mapping, summarize
from sources import ADDITIVE_CONCEPTS, SOURCES

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"
PROCESSED = ROOT / "data" / "processed"
MAPPING = ROOT / "config" / "ambits_comarques.csv"
#: Atur registrat per municipi (SEPE): del primer any de la font a l'últim acabat.
SEPE_PRIMER_ANY = 2006
#: Municipis amb què es compara la mitjana de l'atur amb la de l'EMEX (Idescat):
#: Barcelona, Girona, Lleida, Tarragona i Vilafranca del Penedès.
EMEX_MUNICIPIS = ["080193", "170792", "251207", "431482", "083054"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--refresh", action="store_true", help="ignora la memòria cau i torna a descarregar")
    parser.add_argument("--lang", default="ca", choices=["ca", "es", "en"])
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):  # evita errors d'accents a la consola de Windows
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")

    PROCESSED.mkdir(parents=True, exist_ok=True)
    mapping = pd.read_csv(MAPPING)
    tables: dict[tuple[str, str], pd.DataFrame] = {}
    catalog, errors = [], []

    for name, src in SOURCES.items():
        for geo in src["geos"]:
            print(f"→ {name} / {geo} ...", end=" ", flush=True)
            # Una taula massa gran per a una sola petició es demana a trossos
            # (`trossos`: filtres que s'afegeixen als de la font, un per petició).
            parts = []
            try:
                for tros in src.get("trossos", [{}]):
                    payload = fetch_json(src["stat"], src["node"], src["table"], geo,
                                         filters={**src.get("filters", {}), **tros} or None, lang=args.lang,
                                         cache_dir=RAW, refresh=args.refresh)
                    parts.append(jsonstat_to_df(payload))
            except IdescatAPIError as exc:
                print("ERROR")
                errors.append(f"{name}/{geo}: {exc}")
                continue
            df = pd.concat(parts, ignore_index=True)
            df.insert(0, "source", name)
            out = PROCESSED / f"{name}_{geo}.csv"
            df.to_csv(out, index=False, encoding="utf-8")
            tables[(name, geo)] = df
            catalog.append({
                "source": name, "geo": geo, "file": out.relative_to(ROOT).as_posix(),
                "label": payload.get("label"), "updated": payload.get("updated"),
                "url": build_url(src["stat"], src["node"], src["table"], geo),
                "filters": src.get("filters"), "rows": len(df),
            })
            print(f"{len(df)} files")

    # ---- Atur registrat per municipi (SEPE) i referència de l'EMEX ----------
    anys = range(SEPE_PRIMER_ANY, datetime.now(timezone.utc).year)
    print(f"→ atur registrat (SEPE) / mun {anys[0]}-{anys[-1]} ...", end=" ", flush=True)
    try:
        atur = sepe.extreu(anys, cache_dir=RAW / "sepe", refresh=args.refresh)
        out = PROCESSED / "atur_registrat_municipis.csv"
        atur.to_csv(out, index=False, encoding="utf-8")
        catalog.append({
            "source": "atur_registrat", "geo": "mun", "file": out.relative_to(ROOT).as_posix(),
            "label": "Paro registrado por municipios (SEPE), mitjana anual", "updated": None,
            "url": sepe.url(anys[-1]), "filters": None, "rows": len(atur),
        })
        print(f"{len(atur)} files")
        ref = sepe.referencia_emex(EMEX_MUNICIPIS)
        ref.to_csv(PROCESSED / "ref_emex_atur.csv", index=False, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 -- la resta de l'extracció continua
        print("ERROR")
        errors.append(f"atur_registrat/mun: {exc}")

    # ---- Controls de qualitat ------------------------------------------------
    report = ["# Informe de qualitat de les dades", "",
              f"Extracció: {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC · Font: Idescat", "",
              "## Resum per taula", ""]
    report += [summarize(df, f"{n}/{g}") for (n, g), df in tables.items()]

    report += ["", "## Mapatge comarca → àmbit", ""]
    com_any = next((df for (n, g), df in tables.items() if g == "com"), None)
    issues = check_mapping(com_any, mapping) if com_any is not None else ["No hi ha cap taula comarcal"]
    report += [f"- ⚠️ {i}" for i in issues] or ["- ✅ Totes les comarques tenen àmbit assignat"]

    report += ["", "## Suma de comarques = total d'àmbit", ""]
    for name, concepts in ADDITIVE_CONCEPTS.items():
        if (name, "com") in tables and (name, "at") in tables:
            agg_issues, _ = check_aggregation(tables[(name, "com")], tables[(name, "at")], mapping, concepts)
            report += [f"- ⚠️ {name}: {i}" for i in agg_issues] or [f"- ✅ {name}: quadra"]

    if errors:
        report += ["", "## Errors de descàrrega", ""] + [f"- {e}" for e in errors]

    (PROCESSED / "qa_report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (PROCESSED / "catalog.json").write_text(json.dumps(catalog, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n".join(report))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
