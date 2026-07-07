from dataclasses import dataclass
from typing import List, Dict
from engines.base_engine import BaseEngine, Result, Status
from data import rpa2024_tables as rpa
from engines.display_utils import afficher_tableau_rich


@dataclass
class DonneeEtage:
    nom: str
    numero: int
    hauteur: float
    delta_ex: float
    delta_ey: float


@dataclass
class ResultatEtage:
    nom: str
    numero: int
    hauteur: float
    hi: float
    delta_ex: float
    delta_ix: float
    delta_relx: float
    ratio_x: float
    ok_x: bool
    delta_ey: float
    delta_iy: float
    delta_rely: float
    ratio_y: float
    ok_y: bool


class DisplacementEngine(BaseEngine):
    def __init__(self):
        super().__init__("Deplacements Inter-etages")

    def calculate(self) -> Result:
        etages: List[DonneeEtage] = self.get('etages', [])
        R = self.get('R', 3.5)
        materiau = self.get('materiau', 'Beton arme')

        if not etages:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["Aucun etage defini"]
            )

        limite = rpa.get_drift_limit(materiau)

        resultats: List[ResultatEtage] = []

        for i, etage in enumerate(etages):
            hi = etage.hauteur

            hi_mm = hi * 1000

            delta_ix = R * etage.delta_ex
            delta_iy = R * etage.delta_ey

            if i == 0:
                delta_ix_prec = 0.0
                delta_iy_prec = 0.0
            else:
                delta_ix_prec = R * etages[i-1].delta_ex
                delta_iy_prec = R * etages[i-1].delta_ey

            delta_relx = delta_ix - delta_ix_prec
            delta_rely = delta_iy - delta_iy_prec

            ratio_x = abs(delta_relx) / hi_mm if hi_mm > 0 else 0
            ratio_y = abs(delta_rely) / hi_mm if hi_mm > 0 else 0

            ok_x = ratio_x <= limite
            ok_y = ratio_y <= limite

            resultats.append(ResultatEtage(
                nom=etage.nom, numero=etage.numero,
                hauteur=etage.hauteur, hi=round(hi, 2),
                delta_ex=round(etage.delta_ex, 3),
                delta_ix=round(delta_ix, 3),
                delta_relx=round(delta_relx, 3),
                ratio_x=round(ratio_x * 100, 4),
                ok_x=ok_x,
                delta_ey=round(etage.delta_ey, 3),
                delta_iy=round(delta_iy, 3),
                delta_rely=round(delta_rely, 3),
                ratio_y=round(ratio_y * 100, 4),
                ok_y=ok_y,
            ))

        tous_ok = all(r.ok_x and r.ok_y for r in resultats)

        max_ratio_x = max(resultats, key=lambda r: r.ratio_x)
        max_ratio_y = max(resultats, key=lambda r: r.ratio_y)

        tableau = self._creer_tableau(resultats, limite)

        self.result = Result(
            module=self.name,
            status=Status.OK if tous_ok else Status.FAILED,
            values={
                'R':            R,
                'materiau':     materiau,
                'limite':       limite,
                'limite_pct':   f"{limite * 100:.1f}%",
                'resultats':    resultats,
                'tableau':      tableau,
                'tous_ok':      tous_ok,
                'critique_x':   max_ratio_x.nom,
                'critique_y':   max_ratio_y.nom,
                'max_ratio_x':  f"{max_ratio_x.ratio_x:.4f}%",
                'max_ratio_y':  f"{max_ratio_y.ratio_y:.4f}%",
            },
            formulas=[
                "Deplacements inelastiques : di = R x de",
                "Deplacement relatif : Dk = di(k) - di(k-1)",
                f"Verification : Dk/hk <= {limite*100:.1f}%",
                f"R = {R}",
                f"Materiau : {materiau}",
                f"Limite RPA2024 : {limite*100:.1f}% de hk",
            ]
        )

        return self.result

    def _creer_tableau(self, resultats, limite):
        tableau = []
        for r in resultats:
            tableau.append({
                'Etage':       r.nom,
                'hi (m)':      r.hi,
                'deX (mm)':    r.delta_ex,
                'diX (mm)':    r.delta_ix,
                'DX (mm)':     r.delta_relx,
                'DX/h (%)':    r.ratio_x,
                'Verif. X':    '[OK]' if r.ok_x else '[FAIL]',
                'deY (mm)':    r.delta_ey,
                'diY (mm)':    r.delta_iy,
                'DY (mm)':     r.delta_rely,
                'DY/h (%)':    r.ratio_y,
                'Verif. Y':    '[OK]' if r.ok_y else '[FAIL]',
                '_color': 'green' if (r.ok_x and r.ok_y) else 'red',
            })
        return tableau

    def afficher_tableau(self) -> str:
        """Use display helper to return a printable table. Handles dataclass rows."""
        if not self.result:
            return "Lancez calculate() d'abord"

        # Convert dataclass objects to dicts for the helper
        resultats = self.result.values.get('resultats', [])
        rows = [vars(r) if hasattr(r, '__dict__') else r for r in resultats]

        header = "\n" + "=" * 80 + "\n"
        header += f"  DEPLACEMENTS INTER-ETAGES - Limite = {self.result.values.get('limite_pct')}\n"
        header += "=" * 80 + "\n"

        table_txt = afficher_tableau_rich(rows)

        footer = "\n" + "=" * 80 + "\n"
        footer += f"Resultat global : {'TOUS OK' if self.result.values.get('tous_ok') else 'DEPASSEMENT'}\n"
        footer += f"Etage critique X : {self.result.values.get('critique_x')} ({self.result.values.get('max_ratio_x')})\n"
        footer += f"Etage critique Y : {self.result.values.get('critique_y')} ({self.result.values.get('max_ratio_y')})\n"

        return header + table_txt + footer