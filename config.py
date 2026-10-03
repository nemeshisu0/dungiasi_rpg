"""
config.py
=========
Enum, costanti di bilanciamento e profili di classe.

Modulo di sola configurazione: non dipende da nessun altro modulo del
progetto, quindi puo' essere importato da tutti senza rischi di import
circolari.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum, auto
from typing import Dict


# =====================================================================
# ENUM
# =====================================================================

class Rarity(Enum):
    COMUNE = "Comune"
    RARO = "Raro"
    LEGGENDARIO = "Leggendario"


class ItemType(Enum):
    ARMA = "arma"
    ARMATURA = "armatura"
    CONSUMABILE = "consumabile"
    VARIE = "varie"


class Direction(Enum):
    NORD = "N"
    SUD = "S"
    EST = "E"
    OVEST = "O"


class GameState(Enum):
    MENU = auto()
    SELEZIONE_ZONA = auto()
    ESPLORAZIONE = auto()
    COMBATTIMENTO = auto()
    INVENTARIO = auto()
    GAME_OVER = auto()
    VITTORIA = auto()


class CombatAction(Enum):
    ATTACCA = auto()
    USA_OGGETTO = auto()
    ABILITA_SPECIALE = auto()
    FUGGI = auto()


class PlayerClass(Enum):
    GUERRIERO = "Guerriero"
    MAGO = "Mago"
    CAVALIERE = "Cavaliere"
    MEDICO = "Medico"


class ResourceType(Enum):
    FURIA = "Furia"
    MANA = "Mana"
    STAMINA = "Stamina"


# =====================================================================
# COSTANTI DI BILANCIAMENTO
# =====================================================================

# --- Progressione e combattimento generale ---
EXP_BASE = 40             # exp richiesta per passare dal livello 1 al 2
EXP_GROWTH = 1.35         # fattore di crescita esponenziale per livello
DANNO_VARIANZA = 0.15     # +/-15% di variazione casuale sul danno calcolato
CHANCE_FUGA = 0.5
DROP_CHANCE_DEFAULT = 0.6
MAX_INVENTARIO = 15       # numero massimo di slot inventario del giocatore

# Peso relativo assegnato a ciascuna rarita' nella scelta ponderata dei drop.
RARITY_WEIGHTS: Dict[Rarity, float] = {
    Rarity.COMUNE: 70.0,
    Rarity.RARO: 25.0,
    Rarity.LEGGENDARIO: 5.0,
}

# --- Risorse e abilita' di classe ---
FURIA_PER_ATTACCO = 15            # Guerriero: attacco base
FURIA_PER_DANNO_SUBITO = 10       # Guerriero: ogni colpo incassato
STAMINA_COSTO_ATTACCO = 10        # Cavaliere: attacco base
REGEN_TURNO_MAGO = 3              # MP rigenerati a fine turno
REGEN_TURNO_MEDICO = 2            # MP rigenerati a fine turno
REGEN_TURNO_CAVALIERE = 20        # Stamina rigenerata a fine turno

COLPO_DEVASTANTE_MOLT = 1.8       # moltiplicatore dell'attacco
COLPO_DEVASTANTE_DIFESA = 0.7     # frazione di difesa nemica che mitiga
DARDO_ARCANO_MOLT = 1.4           # danno puro (ignora la difesa)
PRONTO_SOCCORSO_PERC = 0.35       # frazione di HP Max curata

EFFETTO_BALUARDO = "baluardo"     # chiave in Player.effetti_attivi
BALUARDO_DURATA_TURNI = 2
BALUARDO_MOLT_DIFESA = 1.5        # +50% difesa
BALUARDO_PERC_RIFLESSO = 0.25     # 25% del danno subito viene riflesso

# --- Rendering CLI e Companion GUI ---
CHAFA_ARGS_PIXEL_ART = ["--symbols=vhalf", "--dither=none", "--size=40x20"]
CHAFA_ARGS_KITTY = ["-f", "kitty", "--size=40x20"]
GUI_WINDOW_TITLE = "Dungeon Crawler - Asset Viewer"
GUI_WINDOW_SIZE = "400x400"


# =====================================================================
# PROFILI DI CLASSE
# =====================================================================

@dataclass(frozen=True)
class ClassProfile:
    """Statistiche iniziali, crescita per livello e abilita' speciale di
    una PlayerClass. Oggetto di sola configurazione (immutabile)."""
    hp_base: int
    risorsa_tipo: ResourceType
    risorsa_max_base: int
    attacco_base: int
    difesa_base: int
    velocita_base: int
    # incrementi applicati ad ogni level up
    delta_hp: int
    delta_attacco: int
    delta_difesa: int
    delta_risorsa_max: int
    # abilita' speciale
    nome_abilita: str
    costo_risorsa: int
    descrizione_abilita: str


CLASS_PROFILES: Dict[PlayerClass, ClassProfile] = {
    PlayerClass.GUERRIERO: ClassProfile(
        hp_base=70, risorsa_tipo=ResourceType.FURIA, risorsa_max_base=100,
        attacco_base=14, difesa_base=6, velocita_base=8,
        delta_hp=14, delta_attacco=4, delta_difesa=2, delta_risorsa_max=0,
        nome_abilita="Colpo Devastante", costo_risorsa=40,
        descrizione_abilita=(
            "Un fendente carico di rabbia: infligge Attacco*1.8 mitigato "
            "solo dal 70% della difesa nemica. Costa 40 Furia."
        ),
    ),
    PlayerClass.MAGO: ClassProfile(
        hp_base=45, risorsa_tipo=ResourceType.MANA, risorsa_max_base=60,
        attacco_base=16, difesa_base=3, velocita_base=10,
        delta_hp=8, delta_attacco=5, delta_difesa=1, delta_risorsa_max=6,
        nome_abilita="Dardo Arcano", costo_risorsa=15,
        descrizione_abilita=(
            "Un dardo di energia pura che infligge Attacco*1.4 ignorando "
            "totalmente la difesa nemica. Costa 15 Mana."
        ),
    ),
    PlayerClass.CAVALIERE: ClassProfile(
        hp_base=90, risorsa_tipo=ResourceType.STAMINA, risorsa_max_base=100,
        attacco_base=11, difesa_base=10, velocita_base=6,
        delta_hp=16, delta_attacco=2, delta_difesa=4, delta_risorsa_max=0,
        nome_abilita="Baluardo Difensivo", costo_risorsa=35,
        descrizione_abilita=(
            "Alza lo scudo per 2 turni: +50% difesa e ogni colpo subito "
            "viene parzialmente riflesso al nemico. Costa 35 Stamina."
        ),
    ),
    PlayerClass.MEDICO: ClassProfile(
        hp_base=55, risorsa_tipo=ResourceType.MANA, risorsa_max_base=70,
        attacco_base=9, difesa_base=5, velocita_base=9,
        delta_hp=10, delta_attacco=2, delta_difesa=2, delta_risorsa_max=5,
        nome_abilita="Pronto Soccorso", costo_risorsa=12,
        descrizione_abilita=(
            "Cura istantaneamente il 35% degli HP Max del giocatore. "
            "Costa 12 Mana."
        ),
    ),
}
