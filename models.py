"""
models.py
=========
Modelli dati del gioco: Item, DropEntry, Monster, Equipaggiamento,
Player, Area. Nessuna logica di flusso: solo stato e piccole regole locali.
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field, replace
from typing import Any, Dict, List, Optional, Tuple

from config import (
    BALUARDO_MOLT_DIFESA,
    CLASS_PROFILES,
    EFFETTO_BALUARDO,
    MAX_INVENTARIO,
    Direction,
    ItemType,
    PlayerClass,
    Rarity,
    ResourceType,
)
from formulas import exp_richiesta_per_livello
from i18n import (
    get_class_name,
    get_direction_label,
    get_item_type_name,
    get_rarity_name,
    get_resource_name,
    t,
)


@dataclass
class Item:
    id: str
    nome: str
    tipo: ItemType
    rarita: Rarity = Rarity.COMUNE
    sprite_path: str = "assets/items/default.png"
    descrizione: str = ""
    bonus_attacco: int = 0
    bonus_difesa: int = 0
    cura_hp: int = 0
    cura_risorsa: int = 0
    valore: int = 0
    consumabile: bool = False

    def to_render_dict(self) -> Dict[str, Any]:
        """Struttura pronta per il frontend (include sprite_path)."""
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": get_item_type_name(self.tipo),
            "rarita": get_rarity_name(self.rarita),
            "sprite_path": self.sprite_path,
            "descrizione": self.descrizione,
            "bonus_attacco": self.bonus_attacco,
            "bonus_difesa": self.bonus_difesa,
            "cura_hp": self.cura_hp,
            "cura_risorsa": self.cura_risorsa,
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializzazione completa dell'oggetto per il salvataggio."""
        return {
            "id": self.id,
            "nome": self.nome,
            "tipo": self.tipo.value,
            "rarita": self.rarita.value,
            "sprite_path": self.sprite_path,
            "bonus_attacco": self.bonus_attacco,
            "bonus_difesa": self.bonus_difesa,
            "cura_hp": self.cura_hp,
            "cura_risorsa": self.cura_risorsa,
            "consumabile": self.consumabile,
            "valore": self.valore,
            "descrizione": self.descrizione,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Item":
        """Ricostruisce un Item a partire da un dizionario serializzato."""
        tipo_val = d["tipo"]
        tipo = ItemType(tipo_val) if isinstance(tipo_val, str) else tipo_val
        rarita_val = d.get("rarita", Rarity.COMUNE.value)
        rarita = Rarity(rarita_val) if isinstance(rarita_val, str) else rarita_val

        return cls(
            id=d["id"],
            nome=d["nome"],
            tipo=tipo,
            rarita=rarita,
            sprite_path=d.get("sprite_path", "assets/items/default.png"),
            descrizione=d.get("descrizione", ""),
            bonus_attacco=d.get("bonus_attacco", 0),
            bonus_difesa=d.get("bonus_difesa", 0),
            cura_hp=d.get("cura_hp", 0),
            cura_risorsa=d.get("cura_risorsa", 0),
            valore=d.get("valore", 0),
            consumabile=d.get("consumabile", False),
        )


@dataclass
class DropEntry:
    """Una riga di una tabella di drop ponderata."""
    item: Item
    peso: float = 1.0      # peso relativo tra gli oggetti droppabili
    chance: float = 1.0    # probabilita' (0-1) che la riga venga considerata


@dataclass
class Monster:
    id: str
    nome: str
    livello: int
    hp_max: int
    attacco: int
    difesa: int
    exp_reward: int
    sprite_path: str = "assets/monsters/default.png"
    drop_table: List[DropEntry] = field(default_factory=list)
    drop_chance_totale: float = 0.6
    oro_min: int = 0
    oro_max: int = 0
    is_boss: bool = False
    fase: int = 1
    fasi: int = 1
    abilita_boss: str = "Soffio Infernale"
    furia_attivata: bool = False
    hp_corrente: int = field(init=False)

    def __post_init__(self) -> None:
        self.hp_corrente = self.hp_max
        self.fase = 1
        self.furia_attivata = False

    @property
    def is_vivo(self) -> bool:
        return self.hp_corrente > 0

    def subisci_danno(self, danno: float) -> int:
        danno_effettivo = max(1, int(round(danno)))
        self.hp_corrente = max(0, self.hp_corrente - danno_effettivo)
        return danno_effettivo

    def clone_per_incontro(self) -> "Monster":
        """Le Area conservano 'template' di mostro: ad ogni incontro si
        genera una nuova istanza con HP pieni (hp_corrente e' init=False,
        quindi viene ricalcolato da __post_init__)."""
        return replace(self)

    def to_render_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "nome": self.nome, "livello": self.livello,
            "hp_corrente": self.hp_corrente, "hp_max": self.hp_max,
            "sprite_path": self.sprite_path,
            "is_boss": self.is_boss,
            "fase": self.fase,
            "fasi": self.fasi,
            "furia_attivata": self.furia_attivata,
        }


@dataclass
class Equipaggiamento:
    arma: Optional[Item] = None
    armatura: Optional[Item] = None

    def to_dict(self) -> Dict[str, Any]:
        """Serializzazione dell'equipaggiamento."""
        return {
            "arma": self.arma.to_dict() if self.arma else None,
            "armatura": self.armatura.to_dict() if self.armatura else None,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Equipaggiamento":
        """Ricostruisce un Equipaggiamento a partire da dizionario."""
        arma_d = d.get("arma")
        armatura_d = d.get("armatura")
        return cls(
            arma=Item.from_dict(arma_d) if arma_d else None,
            armatura=Item.from_dict(armatura_d) if armatura_d else None,
        )


@dataclass
class Player:
    """Il personaggio del giocatore.

    Le statistiche di base vengono derivate dal `ClassProfile` di `classe`
    in `__post_init__`; i level up applicano poi i delta_* dello stesso
    profilo (vedi `GameEngine._controlla_level_up`).
    """
    nome: str
    classe: PlayerClass = PlayerClass.GUERRIERO
    livello: int = 1
    exp: int = 0
    oro: int = 0
    sprite_path: str = "assets/player/hero.png"
    max_inventario: int = MAX_INVENTARIO
    inventario: List[Item] = field(default_factory=list)
    equip: Equipaggiamento = field(default_factory=Equipaggiamento)

    # calcolati in __post_init__: non si passano al costruttore
    hp_max: int = field(init=False)
    hp_corrente: int = field(init=False)
    attacco_base: int = field(init=False)
    difesa_base: int = field(init=False)
    velocita: int = field(init=False)
    risorsa_tipo: ResourceType = field(init=False)
    risorsa_max: int = field(init=False)
    risorsa_corrente: int = field(init=False)
    # contatori di durata dei buff attivi, es. {"baluardo": 2}
    effetti_attivi: Dict[str, int] = field(default_factory=dict, init=False)

    def __post_init__(self) -> None:
        profilo = CLASS_PROFILES[self.classe]
        salti = self.livello - 1
        self.hp_max = profilo.hp_base + profilo.delta_hp * salti
        self.attacco_base = profilo.attacco_base + profilo.delta_attacco * salti
        self.difesa_base = profilo.difesa_base + profilo.delta_difesa * salti
        self.velocita = profilo.velocita_base
        self.risorsa_tipo = profilo.risorsa_tipo
        self.risorsa_max = profilo.risorsa_max_base + profilo.delta_risorsa_max * salti
        self.hp_corrente = self.hp_max
        self.effetti_attivi = {}
        # Al primo avvio: Furia parte da 0, Mana e Stamina partono dal massimale.
        self.risorsa_corrente = 0 if self.risorsa_tipo == ResourceType.FURIA else self.risorsa_max

    @property
    def is_vivo(self) -> bool:
        return self.hp_corrente > 0

    @property
    def attacco_totale(self) -> int:
        bonus = self.equip.arma.bonus_attacco if self.equip.arma else 0
        return self.attacco_base + bonus

    @property
    def difesa_totale(self) -> int:
        """Difesa effettiva: base + armatura, con +50% se 'baluardo' attivo."""
        bonus = self.equip.armatura.bonus_difesa if self.equip.armatura else 0
        difesa = self.difesa_base + bonus
        if self.effetti_attivi.get(EFFETTO_BALUARDO, 0) > 0:
            difesa = int(round(difesa * BALUARDO_MOLT_DIFESA))
        return difesa

    def inizializza_risorsa_per_incontro(self) -> None:
        """Ad inizio incontro azzera solo la Furia del Guerriero.
        Mana e Stamina conservano il loro valore tra gli incontri."""
        if self.risorsa_tipo == ResourceType.FURIA:
            self.risorsa_corrente = 0

    def guadagna_risorsa(self, quantita: int) -> int:
        prima = self.risorsa_corrente
        self.risorsa_corrente = min(self.risorsa_max, self.risorsa_corrente + quantita)
        return self.risorsa_corrente - prima

    def consuma_risorsa(self, quantita: int) -> int:
        consumato = min(self.risorsa_corrente, quantita)
        self.risorsa_corrente -= consumato
        return consumato

    def subisci_danno(self, danno: float) -> int:
        danno_effettivo = max(1, int(round(danno)))
        self.hp_corrente = max(0, self.hp_corrente - danno_effettivo)
        return danno_effettivo

    def cura(self, quantita: int) -> int:
        prima = self.hp_corrente
        self.hp_corrente = min(self.hp_max, self.hp_corrente + quantita)
        return self.hp_corrente - prima

    def aggiungi_oggetto(self, item: Item) -> None:
        self.inventario.append(item)

    def rimuovi_oggetto(self, item: Item) -> None:
        if item in self.inventario:
            self.inventario.remove(item)

    def equipaggia(self, item: Item) -> Tuple[bool, Optional[Item]]:
        """Equipaggia un'arma o armatura gestendo lo swap automatico.
        Ritorna (successo, oggetto_precedente_rimesso_in_inventario)."""
        if item not in self.inventario:
            return False, None

        precedente: Optional[Item] = None

        if item.tipo == ItemType.ARMA:
            precedente = self.equip.arma
            self.equip.arma = item
        elif item.tipo == ItemType.ARMATURA:
            precedente = self.equip.armatura
            self.equip.armatura = item
        else:
            return False, None

        self.rimuovi_oggetto(item)

        if precedente is not None:
            self.aggiungi_oggetto(precedente)

        return True, precedente

    def disequipaggia(self, slot: str) -> Tuple[bool, Optional[Item], str]:
        """Rimuove l'arma ('arma') o l'armatura ('armatura') e la rimette
        nell'inventario se c'e' spazio sufficiente."""
        slot_norm = slot.strip().lower()
        if slot_norm not in ("arma", "armatura", "weapon", "armor"):
            return False, None, t("slot_invalid", slot=slot)

        item_attivo = self.equip.arma if slot_norm in ("arma", "weapon") else self.equip.armatura
        if item_attivo is None:
            return False, None, t("slot_empty", slot=slot_norm)

        if len(self.inventario) >= self.max_inventario:
            return False, None, t("inventory_full_unequip", used=len(self.inventario), max=self.max_inventario)

        if slot_norm in ("arma", "weapon"):
            self.equip.arma = None
        else:
            self.equip.armatura = None

        self.aggiungi_oggetto(item_attivo)
        return True, item_attivo, t("unequipped_success", item=item_attivo.nome, slot=slot_norm)

    def scarta_oggetto(self, item: Item) -> bool:
        """Rimuove definitivamente un oggetto dall'inventario."""
        if item in self.inventario:
            self.inventario.remove(item)
            return True
        return False

    def to_render_dict(self) -> Dict[str, Any]:
        return {
            "nome": self.nome,
            "classe": get_class_name(self.classe),
            "livello": self.livello,
            "hp_corrente": self.hp_corrente, "hp_max": self.hp_max,
            "attacco": self.attacco_totale, "difesa": self.difesa_totale,
            "velocita": self.velocita,
            "risorsa_nome": get_resource_name(self.risorsa_tipo),
            "risorsa_corrente": self.risorsa_corrente,
            "risorsa_max": self.risorsa_max,
            "effetti_attivi": dict(self.effetti_attivi),
            "exp": self.exp, "exp_richiesta": exp_richiesta_per_livello(self.livello),
            "oro": self.oro, "sprite_path": self.sprite_path,
            "max_inventario": self.max_inventario,
            "inventario_occupato": len(self.inventario),
            "equip": {
                "arma": self.equip.arma.to_render_dict() if self.equip.arma else None,
                "armatura": self.equip.armatura.to_render_dict() if self.equip.armatura else None,
            },
        }

    def to_dict(self) -> Dict[str, Any]:
        """Serializzazione completa del giocatore per il salvataggio."""
        return {
            "nome": self.nome,
            "classe": self.classe.value,
            "livello": self.livello,
            "exp": self.exp,
            "hp_corrente": self.hp_corrente,
            "hp_max": self.hp_max,
            "risorsa_corrente": self.risorsa_corrente,
            "risorsa_max": self.risorsa_max,
            "oro": self.oro,
            "attacco": self.attacco_base,
            "attacco_base": self.attacco_base,
            "difesa": self.difesa_base,
            "difesa_base": self.difesa_base,
            "velocita": self.velocita,
            "sprite_path": self.sprite_path,
            "max_inventario": self.max_inventario,
            "equipaggiamento": self.equip.to_dict(),
            "equip": self.equip.to_dict(),
            "inventario": [i.to_dict() for i in self.inventario],
            "effetti_attivi": dict(self.effetti_attivi),
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Player":
        """Ricostruisce un Player ripristinandone lo stato salvato."""
        classe_val = d["classe"]
        classe = PlayerClass(classe_val) if isinstance(classe_val, str) else classe_val

        player = cls(
            nome=d["nome"],
            classe=classe,
            livello=d.get("livello", 1),
            exp=d.get("exp", 0),
            oro=d.get("oro", 0),
            sprite_path=d.get("sprite_path", "assets/player/hero.png"),
            max_inventario=d.get("max_inventario", MAX_INVENTARIO),
        )

        if "hp_max" in d:
            player.hp_max = d["hp_max"]
        if "hp_corrente" in d:
            player.hp_corrente = d["hp_corrente"]
        if "attacco" in d:
            player.attacco_base = d["attacco"]
        elif "attacco_base" in d:
            player.attacco_base = d["attacco_base"]
        if "difesa" in d:
            player.difesa_base = d["difesa"]
        elif "difesa_base" in d:
            player.difesa_base = d["difesa_base"]
        if "risorsa_max" in d:
            player.risorsa_max = d["risorsa_max"]
        if "risorsa_corrente" in d:
            player.risorsa_corrente = d["risorsa_corrente"]
        if "velocita" in d:
            player.velocita = d["velocita"]

        player.effetti_attivi = dict(d.get("effetti_attivi", {}))
        player.inventario = [Item.from_dict(i) for i in d.get("inventario", [])]

        equip_dict = d.get("equipaggiamento") or d.get("equip")
        if equip_dict:
            player.equip = Equipaggiamento.from_dict(equip_dict)

        return player


@dataclass
class Area:
    id: str
    nome: str
    descrizione: str = ""
    background_sprite_path: str = "assets/areas/default.png"
    uscite: Dict[Direction, str] = field(default_factory=dict)       # direzione -> id Area
    mostri_possibili: List[Monster] = field(default_factory=list)   # template
    chance_incontro: float = 0.4
    oggetti_terra: List[Item] = field(default_factory=list)

    def mostro_casuale(self) -> Optional[Monster]:
        if not self.mostri_possibili:
            return None
        return random.choice(self.mostri_possibili).clone_per_incontro()

    def to_render_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id, "nome": self.nome, "descrizione": self.descrizione,
            "sprite_path": self.background_sprite_path,
            "uscite_disponibili": [get_direction_label(d.value) for d in self.uscite],
        }
