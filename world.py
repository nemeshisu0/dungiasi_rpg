"""
world.py
========
Contenuti di gioco: oggetti, mostri, aree e dungeon.
Supporta la localizzazione bilingue (italiano / inglese) tramite i18n.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from config import Direction, ItemType, Rarity
from i18n import AREA_DATA, ITEM_DATA, MONSTER_DATA, get_language, set_language
from models import Area, DropEntry, Item, Monster

if TYPE_CHECKING:
    from engine import GameEngine


def popola_mondo(engine: "GameEngine", lang: Optional[str] = None) -> None:
    """Registra nell'engine aree, mostri, equipaggiamento e pozioni nella lingua selezionata."""
    if lang is not None:
        set_language(lang)
    l = get_language()

    def item_info(item_id: str) -> dict:
        return ITEM_DATA.get(item_id, {}).get(l, ITEM_DATA.get(item_id, {}).get("it", {"nome": item_id, "desc": ""}))

    def monster_info(mon_id: str) -> dict:
        return MONSTER_DATA.get(mon_id, {}).get(l, MONSTER_DATA.get(mon_id, {}).get("it", {"nome": mon_id}))

    def area_info(area_id: str) -> dict:
        return AREA_DATA.get(area_id, {}).get(l, AREA_DATA.get(area_id, {}).get("it", {"nome": area_id, "desc": ""}))

    # =================================================================
    # ARMI
    # =================================================================
    info = item_info("spada_ferro")
    spada_ferro = Item(
        id="spada_ferro", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/spada_ferro.png",
        bonus_attacco=4, valore=20, descrizione=info["desc"],
    )

    info = item_info("spadone_due_mani")
    spadone_due_mani = Item(
        id="spadone_due_mani", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/spadone_due_mani.png",
        bonus_attacco=10, valore=80, descrizione=info["desc"],
    )

    info = item_info("bastone_legno")
    bastone_legno = Item(
        id="bastone_legno", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/bastone_legno.png",
        bonus_attacco=3, valore=18, descrizione=info["desc"],
    )

    info = item_info("bastone_arcano")
    bastone_arcano = Item(
        id="bastone_arcano", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/bastone_arcano.png",
        bonus_attacco=8, valore=75, descrizione=info["desc"],
    )

    info = item_info("tomo_preghiere")
    tomo_preghiere = Item(
        id="tomo_preghiere", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/tomo_preghiere.png",
        bonus_attacco=3, valore=22, descrizione=info["desc"],
    )

    info = item_info("tomo_santificato")
    tomo_santificato = Item(
        id="tomo_santificato", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/tomo_santificato.png",
        bonus_attacco=7, valore=85, descrizione=info["desc"],
    )

    info = item_info("lancia_guardia")
    lancia_guardia = Item(
        id="lancia_guardia", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/lancia_guardia.png",
        bonus_attacco=4, valore=25, descrizione=info["desc"],
    )

    info = item_info("pugnale_acciaio")
    pugnale_acciaio = Item(
        id="pugnale_acciaio", nome=info["nome"], tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pugnale_acciaio.png",
        bonus_attacco=2, valore=15, descrizione=info["desc"],
    )

    # =================================================================
    # ARMATURE
    # =================================================================
    info = item_info("veste_magica")
    veste_magica = Item(
        id="veste_magica", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/veste_magica.png",
        bonus_difesa=2, valore=15, descrizione=info["desc"],
    )

    info = item_info("veste_runica")
    veste_runica = Item(
        id="veste_runica", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/veste_runica.png",
        bonus_difesa=5, valore=65, descrizione=info["desc"],
    )

    info = item_info("armatura_cuoio")
    armatura_cuoio = Item(
        id="armatura_cuoio", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/armatura_cuoio.png",
        bonus_difesa=4, valore=25, descrizione=info["desc"],
    )

    info = item_info("scudo_legno")
    scudo_legno = Item(
        id="scudo_legno", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/scudo_legno.png",
        bonus_difesa=3, valore=15, descrizione=info["desc"],
    )

    info = item_info("scudo_runico")
    scudo_runico = Item(
        id="scudo_runico", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/scudo_runico.png",
        bonus_difesa=8, valore=75, descrizione=info["desc"],
    )

    info = item_info("corazza_piastre")
    corazza_piastre = Item(
        id="corazza_piastre", nome=info["nome"], tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/corazza_piastre.png",
        bonus_difesa=9, valore=90, descrizione=info["desc"],
    )

    # =================================================================
    # CONSUMABILI (HP, Mana, Stamina) & OGGETTI SPECIALI
    # =================================================================
    info = item_info("pozione_cura")
    pozione_cura = Item(
        id="pozione_cura", nome=info["nome"], tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_cura.png",
        cura_hp=25, consumabile=True, valore=10,
        descrizione=info["desc"],
    )

    info = item_info("pozione_mana")
    pozione_mana = Item(
        id="pozione_mana", nome=info["nome"], tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_mana.png",
        cura_risorsa=25, consumabile=True, valore=15,
        descrizione=info["desc"],
    )

    info = item_info("pozione_stamina")
    pozione_stamina = Item(
        id="pozione_stamina", nome=info["nome"], tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_stamina.png",
        cura_risorsa=35, consumabile=True, valore=12,
        descrizione=info["desc"],
    )

    info = item_info("amuleto_drago")
    amuleto_drago = Item(
        id="amuleto_drago", nome=info["nome"], tipo=ItemType.VARIE,
        rarita=Rarity.LEGGENDARIO, sprite_path="assets/items/amuleto_drago.png",
        valore=500, descrizione=info["desc"],
    )

    # =================================================================
    # MOSTRI
    # =================================================================
    info_m = monster_info("pipistrello")
    pipistrello = Monster(
        id="pipistrello", nome=info_m["nome"], livello=1,
        hp_max=18, attacco=6, difesa=2, exp_reward=10,
        sprite_path="assets/monsters/pipistrello.png",
        oro_min=1, oro_max=4,
        drop_table=[
            DropEntry(item=pozione_cura, peso=2.0, chance=0.5),
            DropEntry(item=pugnale_acciaio, peso=1.0, chance=0.3),
        ],
    )

    info_m = monster_info("goblin")
    goblin = Monster(
        id="goblin", nome=info_m["nome"], livello=1,
        hp_max=25, attacco=8, difesa=3, exp_reward=15,
        sprite_path="assets/monsters/goblin.png",
        oro_min=2, oro_max=8,
        drop_table=[
            DropEntry(item=spada_ferro, peso=1.0, chance=0.35),
            DropEntry(item=veste_magica, peso=1.0, chance=0.3),
            DropEntry(item=pozione_stamina, peso=1.5, chance=0.5),
            DropEntry(item=pozione_cura, peso=2.0, chance=0.6),
        ],
    )

    info_m = monster_info("ragno")
    ragno = Monster(
        id="ragno", nome=info_m["nome"], livello=2,
        hp_max=35, attacco=11, difesa=4, exp_reward=25,
        sprite_path="assets/monsters/ragno.png",
        oro_min=4, oro_max=12,
        drop_table=[
            DropEntry(item=armatura_cuoio, peso=1.0, chance=0.4),
            DropEntry(item=bastone_legno, peso=1.0, chance=0.4),
            DropEntry(item=pozione_cura, peso=2.0, chance=0.7),
        ],
    )

    info_m = monster_info("scheletro")
    scheletro = Monster(
        id="scheletro", nome=info_m["nome"], livello=2,
        hp_max=40, attacco=10, difesa=6, exp_reward=28,
        sprite_path="assets/monsters/scheletro.png",
        oro_min=5, oro_max=15,
        drop_table=[
            DropEntry(item=scudo_legno, peso=1.0, chance=0.4),
            DropEntry(item=lancia_guardia, peso=1.0, chance=0.35),
            DropEntry(item=tomo_preghiere, peso=1.0, chance=0.3),
            DropEntry(item=pozione_stamina, peso=1.5, chance=0.5),
        ],
    )

    info_m = monster_info("orco")
    orco = Monster(
        id="orco", nome=info_m["nome"], livello=3,
        hp_max=60, attacco=14, difesa=6, exp_reward=45,
        sprite_path="assets/monsters/orco.png",
        oro_min=10, oro_max=25,
        drop_table=[
            DropEntry(item=spadone_due_mani, peso=1.0, chance=0.3),
            DropEntry(item=corazza_piastre, peso=0.8, chance=0.25),
            DropEntry(item=pozione_stamina, peso=2.0, chance=0.7),
            DropEntry(item=pozione_cura, peso=2.0, chance=0.8),
        ],
    )

    info_m = monster_info("spettro")
    spettro = Monster(
        id="spettro", nome=info_m["nome"], livello=4,
        hp_max=50, attacco=18, difesa=3, exp_reward=60,
        sprite_path="assets/monsters/spettro.png",
        oro_min=15, oro_max=35,
        drop_table=[
            DropEntry(item=bastone_arcano, peso=1.0, chance=0.35),
            DropEntry(item=veste_runica, peso=1.0, chance=0.35),
            DropEntry(item=tomo_santificato, peso=1.0, chance=0.3),
            DropEntry(item=pozione_mana, peso=2.5, chance=0.85),
        ],
    )

    info_m = monster_info("golem")
    golem = Monster(
        id="golem", nome=info_m["nome"], livello=5,
        hp_max=95, attacco=16, difesa=14, exp_reward=90,
        sprite_path="assets/monsters/golem.png",
        oro_min=25, oro_max=60,
        drop_table=[
            DropEntry(item=scudo_runico, peso=1.5, chance=0.5),
            DropEntry(item=corazza_piastre, peso=1.0, chance=0.4),
            DropEntry(item=pozione_mana, peso=1.5, chance=0.6),
        ],
    )

    info_m = monster_info("drago")
    drago = Monster(
        id="drago", nome=info_m["nome"], livello=8,
        hp_max=180, attacco=25, difesa=14, exp_reward=350,
        sprite_path="assets/monsters/drago.png",
        oro_min=150, oro_max=300,
        is_boss=True, fase=1, fasi=2,
        abilita_boss=info_m.get("abilita_boss", "Soffio Infernale"),
        drop_table=[DropEntry(item=amuleto_drago, peso=1.0, chance=1.0)],
    )

    # =================================================================
    # AREE
    # =================================================================
    info_a = area_info("ingresso")
    ingresso = Area(
        id="ingresso",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/ingresso.png",
        mostri_possibili=[pipistrello, goblin],
        chance_incontro=0.25,
        uscite={Direction.NORD: "atrio"},
    )

    info_a = area_info("atrio")
    atrio = Area(
        id="atrio",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/atrio.png",
        mostri_possibili=[goblin],
        chance_incontro=0.4,
        uscite={
            Direction.SUD: "ingresso",
            Direction.OVEST: "caverne",
            Direction.EST: "cripta",
            Direction.NORD: "sala_guardie",
        },
    )

    info_a = area_info("caverne")
    caverne = Area(
        id="caverne",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/caverne.png",
        mostri_possibili=[pipistrello, ragno],
        chance_incontro=0.55,
        uscite={Direction.EST: "atrio", Direction.NORD: "nido_ragni"},
    )

    info_a = area_info("nido_ragni")
    nido_ragni = Area(
        id="nido_ragni",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/nido_ragni.png",
        mostri_possibili=[ragno],
        chance_incontro=0.65,
        uscite={Direction.SUD: "caverne"},
    )

    info_a = area_info("cripta")
    cripta = Area(
        id="cripta",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/cripta.png",
        mostri_possibili=[scheletro, spettro],
        chance_incontro=0.5,
        uscite={Direction.OVEST: "atrio", Direction.NORD: "catacombe"},
    )

    info_a = area_info("catacombe")
    catacombe = Area(
        id="catacombe",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/catacombe.png",
        mostri_possibili=[scheletro, spettro, orco],
        chance_incontro=0.6,
        uscite={Direction.SUD: "cripta"},
    )

    info_a = area_info("sala_guardie")
    sala_guardie = Area(
        id="sala_guardie",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/sala_guardie.png",
        mostri_possibili=[scheletro, orco],
        chance_incontro=0.5,
        uscite={Direction.SUD: "atrio", Direction.NORD: "corridoio_runico"},
    )

    info_a = area_info("corridoio_runico")
    corridoio_runico = Area(
        id="corridoio_runico",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/corridoio_runico.png",
        mostri_possibili=[orco, golem],
        chance_incontro=0.65,
        uscite={Direction.SUD: "sala_guardie", Direction.NORD: "sala_trono"},
    )

    info_a = area_info("sala_trono")
    sala_trono = Area(
        id="sala_trono",
        nome=info_a["nome"],
        descrizione=info_a["desc"],
        background_sprite_path="assets/areas/sala_trono.png",
        mostri_possibili=[drago],
        chance_incontro=0.85,
        uscite={Direction.SUD: "corridoio_runico"},
    )

    aree = [
        ingresso, atrio, caverne, nido_ragni,
        cripta, catacombe, sala_guardie, corridoio_runico, sala_trono,
    ]

    for area in aree:
        engine.registra_area(area)
