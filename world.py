"""
world.py
========
Contenuti di gioco: oggetti, mostri, aree e dungeon.
Include consumabili per HP, Mana e Stamina.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from config import Direction, ItemType, Rarity
from models import Area, DropEntry, Item, Monster

if TYPE_CHECKING:
    from engine import GameEngine


def popola_mondo(engine: "GameEngine") -> None:
    """Registra nell'engine aree, mostri, equipaggiamento e pozioni."""

    # =================================================================
    # ARMI
    # =================================================================
    spada_ferro = Item(
        id="spada_ferro", nome="Spada di Ferro", tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/spada_ferro.png",
        bonus_attacco=4, valore=20, descrizione="Una solida lama di ferro a un filo.",
    )
    spadone_due_mani = Item(
        id="spadone_due_mani", nome="Spadone a Due Mani", tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/spadone_due_mani.png",
        bonus_attacco=10, valore=80, descrizione="Pesante e devastante, ideale per il Guerriero.",
    )
    bastone_legno = Item(
        id="bastone_legno", nome="Bastone di Frassino", tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/bastone_legno.png",
        bonus_attacco=3, valore=18, descrizione="Canalizza debolmente l'energia magica.",
    )
    bastone_arcano = Item(
        id="bastone_arcano", nome="Bastone delle Maree Arcane", tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/bastone_arcano.png",
        bonus_attacco=8, valore=75, descrizione="Un cristallo brillante amplifica i dardi arcani.",
    )
    tomo_preghiere = Item(
        id="tomo_preghiere", nome="Tomo dei Riti Curativi", tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/tomo_preghiere.png",
        bonus_attacco=3, valore=22, descrizione="Pagine intrise di formule di soccorso.",
    )
    tomo_santificato = Item(
        id="tomo_santificato", nome="Codice della Grazia Divina", tipo=ItemType.ARMA,
        rarita=Rarity.RARO, sprite_path="assets/items/tomo_santificato.png",
        bonus_attacco=7, valore=85, descrizione="Emana calore sacro respingendo le tenebre.",
    )
    lancia_guardia = Item(
        id="lancia_guardia", nome="Lancia della Guardia", tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/lancia_guardia.png",
        bonus_attacco=4, valore=25, descrizione="Asta bilanciata per colpire mantenendo la guardia.",
    )
    pugnale_acciaio = Item(
        id="pugnale_acciaio", nome="Pugnale d'Acciaio", tipo=ItemType.ARMA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pugnale_acciaio.png",
        bonus_attacco=2, valore=15, descrizione="Leggero e maneggevole.",
    )

    # =================================================================
    # ARMATURE
    # =================================================================
    veste_magica = Item(
        id="veste_magica", nome="Tunica del Novizio", tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/veste_magica.png",
        bonus_difesa=2, valore=15, descrizione="Tessuto leggero che non ostacola la concentrazione.",
    )
    veste_runica = Item(
        id="veste_runica", nome="Veste Tessuta di Rune", tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/veste_runica.png",
        bonus_difesa=5, valore=65, descrizione="Simboli protettivi contro incantesimi.",
    )
    armatura_cuoio = Item(
        id="armatura_cuoio", nome="Armatura di Cuoio Indurito", tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/armatura_cuoio.png",
        bonus_difesa=4, valore=25, descrizione="Protegge dagli artigli senza limitare la mobilita'.",
    )
    scudo_legno = Item(
        id="scudo_legno", nome="Scudo di Legno Rinforzato", tipo=ItemType.ARMATURA,
        rarita=Rarity.COMUNE, sprite_path="assets/items/scudo_legno.png",
        bonus_difesa=3, valore=15, descrizione="Asce e denti faticano a penetrare le sue assi.",
    )
    scudo_runico = Item(
        id="scudo_runico", nome="Scudo a Torre Runico", tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/scudo_runico.png",
        bonus_difesa=8, valore=75, descrizione="Una fortezza portatile ideale per sostenere il Baluardo.",
    )
    corazza_piastre = Item(
        id="corazza_piastre", nome="Corazza di Piastre Forgiata", tipo=ItemType.ARMATURA,
        rarita=Rarity.RARO, sprite_path="assets/items/corazza_piastre.png",
        bonus_difesa=9, valore=90, descrizione="Acciaio temprato che attutisce i colpi violenti.",
    )

    # =================================================================
    # CONSUMABILI (HP, Mana, Stamina) & OGGETTI SPECIALI
    # =================================================================
    pozione_cura = Item(
        id="pozione_cura", nome="Pozione Curativa", tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_cura.png",
        cura_hp=25, consumabile=True, valore=10,
        descrizione="Ripristina 25 punti ferita.",
    )
    pozione_mana = Item(
        id="pozione_mana", nome="Elisir di Mana", tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_mana.png",
        cura_risorsa=25, consumabile=True, valore=15,
        descrizione="Ricarica 25 punti Mana.",
    )
    pozione_stamina = Item(
        id="pozione_stamina", nome="Tonico del Vigore", tipo=ItemType.CONSUMABILE,
        rarita=Rarity.COMUNE, sprite_path="assets/items/pozione_stamina.png",
        cura_risorsa=35, consumabile=True, valore=12,
        descrizione="Recupera 35 punti Stamina.",
    )
    amuleto_drago = Item(
        id="amuleto_drago", nome="Amuleto del Drago Ancestrale", tipo=ItemType.VARIE,
        rarita=Rarity.LEGGENDARIO, sprite_path="assets/items/amuleto_drago.png",
        valore=500,
        descrizione="Brilla di una luce rossa eterna, reliquia delle profondita'.",
    )

    # =================================================================
    # MOSTRI
    # =================================================================
    pipistrello = Monster(
        id="pipistrello", nome="Pipistrello Gigante", livello=1,
        hp_max=18, attacco=6, difesa=2, exp_reward=10,
        sprite_path="assets/monsters/pipistrello.png",
        oro_min=1, oro_max=4,
        drop_table=[
            DropEntry(item=pozione_cura, peso=2.0, chance=0.5),
            DropEntry(item=pugnale_acciaio, peso=1.0, chance=0.3),
        ],
    )

    goblin = Monster(
        id="goblin", nome="Goblin Esploratore", livello=1,
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

    ragno = Monster(
        id="ragno", nome="Ragno Velenoso", livello=2,
        hp_max=35, attacco=11, difesa=4, exp_reward=25,
        sprite_path="assets/monsters/ragno.png",
        oro_min=4, oro_max=12,
        drop_table=[
            DropEntry(item=armatura_cuoio, peso=1.0, chance=0.4),
            DropEntry(item=bastone_legno, peso=1.0, chance=0.4),
            DropEntry(item=pozione_cura, peso=2.0, chance=0.7),
        ],
    )

    scheletro = Monster(
        id="scheletro", nome="Guardiano Scheletrico", livello=2,
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

    orco = Monster(
        id="orco", nome="Orco Guerriero", livello=3,
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

    spettro = Monster(
        id="spettro", nome="Spettro Tormentato", livello=4,
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

    golem = Monster(
        id="golem", nome="Golem di Pietra", livello=5,
        hp_max=95, attacco=16, difesa=14, exp_reward=90,
        sprite_path="assets/monsters/golem.png",
        oro_min=25, oro_max=60,
        drop_table=[
            DropEntry(item=scudo_runico, peso=1.5, chance=0.5),
            DropEntry(item=corazza_piastre, peso=1.0, chance=0.4),
            DropEntry(item=pozione_mana, peso=1.5, chance=0.6),
        ],
    )

    drago = Monster(
        id="drago", nome="Drago Ancestrale", livello=8,
        hp_max=180, attacco=25, difesa=14, exp_reward=350,
        sprite_path="assets/monsters/drago.png",
        oro_min=150, oro_max=300,
        is_boss=True, fase=1, fasi=2,
        abilita_boss="Soffio Infernale",
        drop_table=[DropEntry(item=amuleto_drago, peso=1.0, chance=1.0)],
    )

    # =================================================================
    # AREE
    # =================================================================
    aree = [
        Area(
            id="ingresso",
            nome="Ingresso del Dungeon",
            descrizione="Un massiccio cancello di pietra logorato dai secoli. Verso nord le tenebre si infittiscono.",
            background_sprite_path="assets/areas/ingresso.png",
            mostri_possibili=[pipistrello, goblin],
            chance_incontro=0.25,
            uscite={Direction.NORD: "atrio"},
        ),
        Area(
            id="atrio",
            nome="Atrio dei Bivi",
            descrizione="Un'ampia sala circolare con colonne spezzate. Cunicoli scavati nella roccia si diramano a est e ovest.",
            background_sprite_path="assets/areas/atrio.png",
            mostri_possibili=[goblin],
            chance_incontro=0.4,
            uscite={
                Direction.SUD: "ingresso",
                Direction.OVEST: "caverne",
                Direction.EST: "cripta",
                Direction.NORD: "sala_guardie",
            },
        ),
        Area(
            id="caverne",
            nome="Caverne Umide",
            descrizione="Stalattiti gocciolano dal soffitto. L'aria odora di terra umida e muschio fungino.",
            background_sprite_path="assets/areas/caverne.png",
            mostri_possibili=[pipistrello, ragno],
            chance_incontro=0.55,
            uscite={Direction.EST: "atrio", Direction.NORD: "nido_ragni"},
        ),
        Area(
            id="nido_ragni",
            nome="Nido dei Ragni",
            descrizione="Fitte ragnatele bianche ricoprono pareti e vecchi resti di scheletri appesi.",
            background_sprite_path="assets/areas/nido_ragni.png",
            mostri_possibili=[ragno],
            chance_incontro=0.65,
            uscite={Direction.SUD: "caverne"},
        ),
        Area(
            id="cripta",
            nome="Cripta Dimenticata",
            descrizione="Sarcofagi aperti e polvere d'ossa. Una brezza gelida spegne quasi il chiarore delle torce.",
            background_sprite_path="assets/areas/cripta.png",
            mostri_possibili=[scheletro, spettro],
            chance_incontro=0.5,
            uscite={Direction.OVEST: "atrio", Direction.NORD: "catacombe"},
        ),
        Area(
            id="catacombe",
            nome="Catacombe Profonde",
            descrizione="Loculi scavati nel tufo su ogni parete. Si sentono lamenti soffusi in lontananza.",
            background_sprite_path="assets/areas/catacombe.png",
            mostri_possibili=[scheletro, spettro, orco],
            chance_incontro=0.6,
            uscite={Direction.SUD: "cripta"},
        ),
        Area(
            id="sala_guardie",
            nome="Sala delle Guardie",
            descrizione="Tavolacci ribaltati e scudi spezzati testimoniano un'antica guarnigione caduta in battaglia.",
            background_sprite_path="assets/areas/sala_guardie.png",
            mostri_possibili=[scheletro, orco],
            chance_incontro=0.5,
            uscite={Direction.SUD: "atrio", Direction.NORD: "corridoio_runico"},
        ),
        Area(
            id="corridoio_runico",
            nome="Corridoio delle Rune",
            descrizione="Pietre megalitiche incise di glifi luminosi. L'accesso alle profondita' e' difeso da colossi di pietra.",
            background_sprite_path="assets/areas/corridoio_runico.png",
            mostri_possibili=[orco, golem],
            chance_incontro=0.65,
            uscite={Direction.SUD: "sala_guardie", Direction.NORD: "sala_trono"},
        ),
        Area(
            id="sala_trono",
            nome="Sala del Trono Ancestrale",
            descrizione="Un'immensa caverna con un trono dorato in rovina. Un colossale drago dorme circondato da tesori.",
            background_sprite_path="assets/areas/sala_trono.png",
            mostri_possibili=[drago],
            chance_incontro=0.85,
            uscite={Direction.SUD: "corridoio_runico"},
        ),
    ]

    for area in aree:
        engine.registra_area(area)
