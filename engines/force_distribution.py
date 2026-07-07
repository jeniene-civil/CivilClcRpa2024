from dataclasses import dataclass
from typing import List
from engines.base_engine import BaseEngine, Result, Status
from engines.display_utils import afficher_tableau_rich


@dataclass
class Etage:
    nom: str
    numero: int
    hauteur: float
    masse: float

    @property
    def poids(self) -> float:
        return self.masse * 9.81


class ForceDistributionEngine(BaseEngine):
    def __init__(self):
        super().__init__("Distribution des Forces")

    def calculate(self) -> Result:
        etages: List[Etage] = self.get('etages', [])
        V_base = self.get('V_base', 0.0)
        T = self.get('T', 0.0)

        if not etages:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["Aucun etage defini"]
            )

        if V_base <= 0:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["V_base doit etre > 0"]
            )

        if T > 0.7:
            Ft = 0.07 * T * V_base
            Ft = min(Ft, 0.25 * V_base)
        else:
            Ft = 0.0

        V_a_distribuer = V_base - Ft

        wh_produits = []
        elevations = []
        Hi_cum = 0.0
        for e in etages:
            Hi_cum += e.hauteur
            elevations.append(Hi_cum)
            wh = e.poids * Hi_cum
            wh_produits.append(wh)

        somme_wh = sum(wh_produits)

        if somme_wh == 0:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["Somme WixHi = 0, verifiez les donnees"]
            )

        resultats_etages = []
        V_cumulatif = V_base

        for i, etage in enumerate(etages):
            Fi = V_a_distribuer * (wh_produits[i] / somme_wh)

            est_sommet = (i == len(etages) - 1)
            if est_sommet:
                Fi += Ft

            hi_etage = etage.hauteur

            Vi = V_cumulatif
            V_cumulatif -= Fi

            resultats_etages.append({
                'Etage':      etage.nom,
                'N':         etage.numero,
                'Hi (m)':     round(elevations[i], 2),
                'hi (m)':     round(hi_etage, 2),
                'Wi (kN)':    round(etage.poids, 2),
                'WixHi':      round(wh_produits[i], 2),
                'Fi (kN)':    round(Fi, 2),
                'Vi (kN)':    round(Vi, 2),
                'Ft':         round(Ft, 2) if est_sommet else 0.0,
            })

        somme_Fi = sum(r['Fi (kN)'] for r in resultats_etages)
        controle_ok = abs(somme_Fi - V_base) < 0.1

        self.result = Result(
            module=self.name,
            status=Status.OK if controle_ok else Status.WARNING,
            values={
                'V_base':           round(V_base, 2),
                'Ft_sommet':        round(Ft, 2),
                'V_distribue':      round(V_a_distribuer, 2),
                'Somme_WiHi':       round(somme_wh, 2),
                'etages':           resultats_etages,
                'Somme_Fi':         round(somme_Fi, 2),
                'Controle_OK':      controle_ok,
            },
            formulas=[
                "Distribution RPA2024 : Fi = V x (WixHi) / Sum(WjxHj)",
                f"V_base = {V_base:.2f} kN",
                f"T = {T:.3f} s",
                f"Ft (sommet) = {Ft:.2f} kN"
                if Ft > 0 else "Ft = 0 (T <= 0.7s)",
                f"V a distribuer = {V_a_distribuer:.2f} kN",
                f"Sum(WixHi) = {somme_wh:.2f} kN.m",
                f"Verification Sum Fi = {somme_Fi:.2f} ~ {V_base:.2f} kN",
            ]
        )

        return self.result

    def afficher_tableau(self) -> str:
        """Return a printable table for the distributed forces using the display helper."""
        if not self.result:
            return "Aucun resultat. Lancez calculate() d'abord."

        etages = self.result.values.get('etages', [])

        # Use the rich/text helper to format the list of dicts
        table_txt = afficher_tableau_rich(etages)

        # Add a small header and totals summary
        total_W = sum(e['Wi (kN)'] for e in etages) if etages else 0.0
        total_F = sum(e['Fi (kN)'] for e in etages) if etages else 0.0

        header = "\n" + "=" * 75 + "\n  DISTRIBUTION DES FORCES\n" + "=" * 75 + "\n"
        footer = "\n" + "=" * 75 + "\n"
        footer += f"TOTAL   Wi (kN): {total_W:.2f}   Somme Fi (kN): {total_F:.2f}\n"
        footer += "=" * 75 + "\n"

        return header + table_txt + footer