# PR description placeholder

This PR adds a robust display helper for engines (engines/display_utils.py)
and updates several engine modules to return printable strings from
`afficher_tableau()` / `afficher_resultat()`.

The helper supports pandas.DataFrame, list[dict], list[list|tuple], dict
and will use `rich` for formatting when available.

Changes:
- Added: engines/display_utils.py
- Updated: engines/force_distribution.py, engines/displacement.py, engines/pdelta.py, engines/overturning.py

Please review and merge if OK.
