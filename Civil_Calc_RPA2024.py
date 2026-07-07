#!/usr/bin/env python
"""
Civil_Calc_RPA2024.py - Lanceur modulaire RPA2024

Utilisation :
    python Civil_Calc_RPA2024.py

Pour utiliser les moteurs individuellement :
    from engines.spectrum import SpectrumEngine
    from engines.base_shear import BaseShearEngine
    from engines.force_distribution import ForceDistributionEngine, Etage
    from data import rpa2024_tables as rpa
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    from tests.test_moteurs import (
        test_spectre, test_effort_tranchant, test_distribution,
        separateur
    )
    from engines.base_engine import Status

    res_spectre = test_spectre()
    res_shear = test_effort_tranchant()

    if res_shear.status != Status.FAILED:
        V = res_shear.values['V_final']
        T = res_shear.values['T_utilisee']
        test_distribution(V, T)

    separateur("TOUS LES TESTS TERMINES")
    print("\nSucces !")
