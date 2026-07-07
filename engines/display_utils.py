# engines/display_utils.py
from typing import Any
from io import StringIO


def _dataframe_to_text(df) -> str:
    try:
        return df.to_string(index=False)
    except Exception:
        return str(df)


def afficher_tableau_generic(data: Any) -> str:
    """
    Retourne toujours une str représentant le tableau.
    Gère pandas.DataFrame, list[dict], list[list|tuple], dict ou str.
    """
    try:
        import pandas as pd
    except Exception:
        pd = None

    if data is None:
        return ""

    if pd is not None and isinstance(data, pd.DataFrame):
        return _dataframe_to_text(data)

    if isinstance(data, list) and data and isinstance(data[0], dict) and pd is not None:
        df = pd.DataFrame(data)
        return _dataframe_to_text(df)

    if isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        cols = list(zip(*data))
        col_widths = [max(len(str(x)) for x in c) for c in cols]
        lines = []
        for row in data:
            parts = []
            for i, val in enumerate(row):
                parts.append(str(val).ljust(col_widths[i]))
            lines.append(" | ".join(parts))
        return "\n".join(lines)

    if isinstance(data, dict):
        return "\n".join(f"{k}: {v}" for k, v in data.items())

    if isinstance(data, str):
        return data

    try:
        return str(data)
    except Exception:
        return ""


def afficher_tableau_rich(data: Any) -> str:
    """
    Si rich est installé, construit une table et renvoie le rendu texte,
    sinon fallback sur afficher_tableau_generic.
    """
    try:
        from rich.console import Console
        from rich.table import Table
    except Exception:
        return afficher_tableau_generic(data)

    console = Console(record=True, force_terminal=True)
    table = Table(show_header=True)

    try:
        import pandas as pd
    except Exception:
        pd = None

    if pd is not None and isinstance(data, pd.DataFrame):
        headers = list(data.columns)
        for h in headers:
            table.add_column(str(h))
        for _, row in data.iterrows():
            table.add_row(*[str(x) for x in row.tolist()])
    elif isinstance(data, list) and data and isinstance(data[0], dict):
        headers = list(data[0].keys())
        for h in headers:
            table.add_column(str(h))
        for r in data:
            table.add_row(*[str(r.get(h, "")) for h in headers])
    elif isinstance(data, list) and data and isinstance(data[0], (list, tuple)):
        n = len(data[0])
        for i in range(n):
            table.add_column(f"C{i+1}")
        for r in data:
            table.add_row(*[str(x) for x in r])
    elif isinstance(data, dict):
        table.add_column("Clé")
        table.add_column("Valeur")
        for k, v in data.items():
            table.add_row(str(k), str(v))
    else:
        console.print(str(data))
        return console.export_text()

    console.print(table)
    return console.export_text()


def afficher_resultat_generic(values: Any) -> str:
    """
    Retourne une synthèse textuelle des résultats (dict attendu).
    """
    if values is None:
        return ""
    if isinstance(values, dict):
        return "\n".join(f"{k}: {v}" for k, v in values.items())
    return str(values)
