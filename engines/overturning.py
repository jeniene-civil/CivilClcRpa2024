from typing import List
from engines.base_engine import BaseEngine, Result, Status
from engines.display_utils import afficher_tableau_rich


class OverturningEngine(BaseEngine):
    def __init__(self):
        super().__init__("Renversement")

    def calculate(self) -> Result:
        forces = self.get('forces_etages', [])
        L = self.get('L_bat', 0)
        l = self.get('l_bat', 0)
        W_total = self.get('W_total', 0)
        direction = self.get('direction', 'X')

        if not forces or W_total <= 0:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["Donnees manquantes"]
            )

        detail_mr = []
        Mr = 0.0

        for etage in forces:
            Fi = etage.get('Fi', 0)
            Hi = etage.get('Hi', 0)
            contribution = Fi * Hi
            Mr += contribution
            detail_mr.append({
                'Etage':     etage.get('nom', ''),
                'Fi (kN)':   round(Fi, 2),
                'Hi (m)':    round(Hi, 2),
                'FixHi':     round(contribution, 2),
            })

        B = L if direction == 'X' else l
        Ms = W_total * (B / 2)

        ratio = Ms / Mr if Mr > 0 else float('inf')
        verifie = ratio >= 1.0

        self.result = Result(
            module=self.name,
            status=Status.OK if verifie else Status.FAILED,
            values={
                'direction':    direction,
                'Mr':           round(Mr, 2),
                'Ms':           round(Ms, 2),
                'ratio_Ms_Mr':  round(ratio, 3),
                'verifie':      verifie,
                'W_total':      W_total,
                'B':            B,
                'detail_mr':    detail_mr,
            },
            formulas=[
                "Mr = Sum (Fi x Hi)",
                "Ms = W_total x (B / 2)",
                "Verification : Ms / Mr >= 1.0",
                f"Mr = {round(Mr, 2)} kN.m",
                f"Ms = {W_total} x {B/2} = {round(Ms, 2)} kN.m",
                f"Ratio = {round(ratio, 3)}",
                f"{('[OK] VERIFIE (Ms >= Mr)' if verifie else '[FAIL] NON VERIFIE (Ms < Mr)')}",
            ]
        )

        return self.result

    def afficher_resultat(self) -> str:
        if not self.result:
            return "Lancez calculate() d'abord"

        v = self.result.values
        header = "\n" + "=" * 55 + "\n  RENVERSEMENT - Direction " + str(v.get('direction')) + "\n" + "=" * 55 + "\n"
        detail_txt = afficher_tableau_rich(v.get('detail_mr', []))

        summary = []
        summary.append("\n")
        summary.append(f"Mr TOTAL : {v.get('Mr'):.2f} kN.m")
        summary.append(f"Ms = {v.get('W_total')} x {v.get('B')/2:.2f}")
        summary.append(f"Ms = {v.get('Ms'):.2f} kN.m")
        summary.append(f"Ratio Ms/Mr = {v.get('ratio_Ms_Mr')}")
        summary.append(f"Resultat : {'[OK] VERIFIE' if v.get('verifie') else '[FAIL] NON VERIFIE'}")

        footer = "\n" + "=" * 55 + "\n"

        return header + detail_txt + "\n" + "\n".join(summary) + footer