"""
formulas.py
===========
Funzioni pure di calcolo: mitigazione del danno, curva EXP, drop ponderati.

Dipende solo da `config`. I modelli sono importati esclusivamente per i
type hint (blocco TYPE_CHECKING), cosi' non si creano import circolari con
`models`, che a sua volta usa `exp_richiesta_per_livello`.
"""

from __future__ import annotations

import math
import random
from typing import TYPE_CHECKING, List

from config import (
    DANNO_VARIANZA,
    DROP_CHANCE_DEFAULT,
    EXP_BASE,
    EXP_GROWTH,
    RARITY_WEIGHTS,
)

if TYPE_CHECKING:
    from models import DropEntry, Item


def calcola_danno(attacco: float, difesa: float, varianza: float = DANNO_VARIANZA) -> float:
    """Formula di mitigazione del danno:

        Danno = Attacco * (100 / (100 + Difesa))

    con una piccola variazione casuale (+/- varianza). Il risultato non e'
    arrotondato: se ne occupa `subisci_danno` di Player/Monster.
    """
    danno_base = attacco * (100.0 / (100.0 + max(0.0, difesa)))
    return danno_base * random.uniform(1 - varianza, 1 + varianza)


def exp_richiesta_per_livello(livello: int) -> int:
    """Curva EXP esponenziale: exp necessaria per salire dal livello
    indicato a quello successivo."""
    return math.floor(EXP_BASE * (EXP_GROWTH ** (livello - 1)))


def tira_drop(drop_table: List["DropEntry"], drop_chance_totale: float = DROP_CHANCE_DEFAULT) -> List["Item"]:
    """Determina l'eventuale drop di un mostro.

    1. Si tira per stabilire SE avviene un drop (drop_chance_totale).
    2. Ogni riga della tabella supera un proprio tiro `chance`.
    3. Tra i candidati si sceglie UN oggetto con peso
       `entry.peso * RARITY_WEIGHTS[rarita]`: i Leggendari, pur presenti,
       escono molto piu' raramente dei Comuni.
    """
    if not drop_table or random.random() > drop_chance_totale:
        return []

    candidati = [e for e in drop_table if random.random() <= e.chance]
    if not candidati:
        return []

    pesi = [e.peso * RARITY_WEIGHTS.get(e.item.rarita, 1.0) for e in candidati]
    scelto = random.choices([e.item for e in candidati], weights=pesi, k=1)[0]
    return [scelto]
