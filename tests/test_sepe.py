"""Proves de la lectura de l'atur registrat del SEPE (sense connexió).

Executa des de l'arrel:  python -m pytest tests
"""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sepe import llegeix, mitjana_anual  # noqa: E402

CAPCALERA = (
    ";;;;PARO REGISTRADO POR MUNICIPIOS DESGLOSADO POR SEXO, TRAMOS DE EDAD Y SECTOR DE LA ACTIVIDAD ECONÓMICA;;;;;;;;;;;;;;;\r\n"
    "Código mes ;mes;Código de CA;Comunidad Autónoma;Codigo Provincia;Provincia;Codigo Municipio; Municipio;"
    "total Paro Registrado;Paro hombre edad < 25;Paro hombre edad 25 -45 ;Paro hombre edad >=45;Paro mujer edad < 25;"
    "Paro mujer edad 25 -45 ;Paro mujer edad >=45;Paro Agricultura;Paro Industria;Paro Construcción;Paro Servicios;"
    "Paro Sin empleo Anterior\r\n"
)


def fila(mes: str, ca: str, municipi: str, nom: str, total: str) -> str:
    return f"{mes};mes;{ca};CA;8;Barcelona;{municipi};{nom};{total};1;1;1;1;1;1;1;1;1;1;1\r\n"


def fitxer(files: list[str]) -> bytes:
    return (CAPCALERA + "".join(files)).encode("latin1")


def any_sencer(any_: int, municipi: str, nom: str, totals: list[str]) -> list[str]:
    return [fila(f"{any_}{m:02d}", "9", municipi, nom, t) for m, t in enumerate(totals, start=1)]


def test_nomes_catalunya_i_codi_de_cinc_xifres():
    d = llegeix(fitxer([fila("200601", "9", "8305", "Vilafranca del Penedès", "100"),
                        fila("200601", "1", "4001", "Abla", "56")]))
    assert d["municipi_code"].tolist() == ["08305"]
    assert d["municipi"].tolist() == ["Vilafranca del Penedès"]
    assert d["total"].tolist() == [100]


def test_menys_de_5_queda_buit_i_marcat():
    d = llegeix(fitxer([fila("202401", "9", "08001", "Abrera", "<5")]))
    assert pd.isna(d["total"].iloc[0])
    assert bool(d["menys_de_5"].iloc[0])


def test_mitjana_anual_de_dotze_mesos():
    a = mitjana_anual(llegeix(fitxer(any_sencer(2024, "08305", "Vilafranca", [str(100 + m) for m in range(12)]))))
    assert a["valor"].item() == 105.5
    assert a["mesos"].item() == 12
    assert a["estat"].item() == ""


def test_un_mes_amagat_no_dona_mitjana():
    totals = ["10"] * 11 + ["<5"]
    a = mitjana_anual(llegeix(fitxer(any_sencer(2024, "08001", "Abrera", totals))))
    assert pd.isna(a["valor"].item())
    assert a["estat"].item() == "<5"


def test_any_amb_un_mes_menys_es_marca():
    a = mitjana_anual(llegeix(fitxer(any_sencer(2020, "08305", "Vilafranca", ["100"] * 11))))
    assert a["valor"].item() == 100
    assert a["estat"].item() == "11m"


def test_any_amb_pocs_mesos_no_dona_mitjana():
    a = mitjana_anual(llegeix(fitxer(any_sencer(2013, "08305", "Vilafranca", ["100"] * 4))))
    assert pd.isna(a["valor"].item())
    assert a["estat"].item() == "4m"
