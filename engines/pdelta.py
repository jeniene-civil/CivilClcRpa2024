from dataclasses import dataclass
from typing import List
from engines.base_engine import BaseEngine, Result, Status


@dataclass
class DonneePDelta:
    nom: str
    numero: int
    hi: float
    Pk: float
    Vk: float
    delta_k: float


class PDeltaEngine(BaseEngine):
    LIMITE_NEGLIGEABLE = 0.10
    LIMITE_ACCEPTABLE  = 0.20

    def __init__(self):
        super().__init__("Effet P-Delta")

    def calculate(self) -> Result:
        etages: List[DonneePDelta] = self.get('etages_pdelta', [])

        if not etages:
            return Result(
                module=self.name,
                status=Status.FAILED,
                warnings=["Aucun etage defini"]
            )

        resultats = []
        statut_global = Status.OK

        for etage in etages:
            delta_m = etage.delta_k / 1000

            if etage.Vk > 0 and etage.hi > 0:
                theta = (etage.Pk * delta_m) / (etage.Vk * etage.hi)
            else:
                theta = 0.0

            statut, couleur, action = self._classifier(theta)

            if statut == '[FAIL] Reviser':
                statut_global = Status.FAILED
            elif (statut == '[!] A prendre en compte'
                  and statut_global == Status.OK):
                statut_global = Status.WARNING

            resultats.append({
                'Etage':        etage.nom,
                'N':           etage.numero,
                'hi (m)':       round(etage.hi, 2),
                'Pk (kN)':      round(etage.Pk, 2),
                'Dk (mm)':      round(etage.delta_k, 3),
                'Vk (kN)':      round(etage.Vk, 2),
                'thetak':       round(theta, 4),
                'Statut':       statut,
                'Action':       action,
                '_color':       couleur,
            })

        theta_max = max(r['thetak'] for r in resultats)
        etage_critique = next(
            r['Etage'] for r in resultats if r['thetak'] == theta_max
        )

        self.result = Result(
            module=self.name,
            status=statut_global,
            values={
                'resultats':       resultats,
                'theta_max':       round(theta_max, 4),
                'etage_critique':  etage_critique,
                'limite_1':        self.LIMITE_NEGLIGEABLE,
                'limite_2':        self.LIMITE_ACCEPTABLE,
            },
            formulas=[
                "thetak = (Pk x Dk) / (Vk x hk)",
                "Pk = Poids cumule au-dessus de l'etage k",
                "Dk = Deplacement relatif inelastique (m)",
                "Vk = Effort tranchant a l'etage k",
                "hk = Hauteur de l'etage k",
                f"theta <= {self.LIMITE_NEGLIGEABLE} -> Negligeable",
                f"{self.LIMITE_NEGLIGEABLE} < theta <= "
                f"{self.LIMITE_ACCEPTABLE} -> A prendre en compte",
                f"theta > {self.LIMITE_ACCEPTABLE} -> Reviser structure",
            ]
        )

        return self.result

    def _classifier(self, theta: float):
        if theta <= self.LIMITE_NEGLIGEABLE:
            return ("[OK] Negligeable", "green", "Aucune action requise")
        elif theta <= self.LIMITE_ACCEPTABLE:
            return ("[!] A prendre en compte", "orange",
                    "Amplifier les forces par 1/(1-theta)")
        else:
            return ("[FAIL] Reviser", "red",
                    "Rigidifier la structure (augmenter voiles)")

    def get_amplification_factor(self, theta: float) -> float:
        if theta <= 0:
            return 1.0
        return round(1 / (1 - theta), 4)

    def afficher_tableau(self) -> str:
        if not self.result:
            return "Lancez calculate() d'abord"

        resultats = self.result.values.get('resultats', [])
        header = "\n" + "=" * 75 + "\n  EFFET P-DELTA - RPA2024\n" + "=" * 75 + "\n"
        # Use display_utils if available
        try:
            from engines.display_utils import afficher_tableau_rich
            table_txt = afficher_tableau_rich(resultats)
        except Exception:
            # Fallback to simple text
            lines = []
            lines.append(f"{'Etage':<8} {'hi(m)':>6} {'Pk(kN)':>10} {'Dk(mm)':>8} {'Vk(kN)':>10} {'thetak':>8} {'Statut':<25}")
            lines.append("-" * 75)
            for r in resultats:
                lines.append(
                    f"{r['Etage']:<8} {r['hi (m)']:>6.2f} {r['Pk (kN)']:>10.2f} {r['Dk (mm)']:>8.3f} {r['Vk (kN)']:>10.2f} {r['thetak']:>8.4f} {r['Statut']:<25}"
                )
            table_txt = "\n".join(lines)
        footer = "\n" + "=" * 75 + "\n"
        footer += f"theta maximum : {self.result.values.get('theta_max')} (Etage {self.result.values.get('etage_critique')})\n"
        return header + table_txt + footer