"""Gemeinsame Fixtures: die Mini-Instanz, an der jede Einheit von Hand geprüft wird (DEMO-PLAYBOOK §1b)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rgv_scenario import Instance  # noqa: E402


@pytest.fixture
def mini():
    """Sechs Rechtecke (Breite, Höhe) = (6, 4), (5, 3), (3, 2), (4, 3), (4, 3), (4, 2) mit den Nummern 0 bis 5, Behälter 10 mal 10, Fläche 77, Schranke 1.

    Von Hand gerechnet (Details in tests/test_algorithm.py): Next Fit in Lieferreihenfolge braucht 2 Behälter, First Fit in Lieferreihenfolge 1; Optimum 1."""
    return Instance(((6, 4), (5, 3), (3, 2), (4, 3), (4, 3), (4, 2)), 10)
