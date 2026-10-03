"""
i18n.py
=======
Sistema di internazionalizzazione (i18n) per Dungiasi RPG.
Supporta Italiano (it) e Inglese (en).
"""

from __future__ import annotations

from typing import Any, Dict, Optional
from config import PlayerClass, ResourceType, Rarity, ItemType, Direction

_CURRENT_LANG: str = "it"


def set_language(lang: str) -> None:
    """Imposta la lingua corrente ('it' o 'en')."""
    global _CURRENT_LANG
    lang_norm = lang.strip().lower()
    if lang_norm in ("en", "english", "inglese", "2"):
        _CURRENT_LANG = "en"
    else:
        _CURRENT_LANG = "it"


def get_language() -> str:
    """Restituisce il codice della lingua corrente ('it' o 'en')."""
    return _CURRENT_LANG


# =====================================================================
# DIZIONARIO TRADUZIONI DI SISTEMA E UI
# =====================================================================

TEXTS: Dict[str, Dict[str, str]] = {
    "it": {
        # Menu Principale e Avvio
        "game_title": "=== DUNGIASI RPG ===",
        "menu_new_game": "[1] Nuova Partita",
        "menu_load_game": "[2] Carica Partita",
        "menu_quit": "[q] Esci",
        "choice_prompt": "Scelta: ",
        "invalid_choice": "Scelta non valida. Opzioni: {options}",
        "farewell": "\nA presto, avventuriero!",
        "hero_name_prompt": "\nNome dell'eroe: ",
        "default_hero_name": "Eroe",
        "starting_new_game": "Avvio di una nuova partita...",
        "select_class_title": "\nScegli la tua classe:",
        "class_prompt": "Classe (numero): ",
        "select_zone_title": "\nZone disponibili:",
        "zone_prompt": "Zona (numero): ",
        
        # UI di Stato
        "backpack_slot": "Zaino {used}/{max} slot",
        "backpack_stats": "Zaino: {used}/{max} slot",
        "stats_hp": "HP",
        "active_effects": "Effetti: {effects}",
        "turns_suffix": "{count} turni",
        "exits": "Uscite:",
        "asset_viewer_title": "Dungiasi RPG - Asset Viewer",
        "waiting_event": "(In attesa del primo evento di gioco...)",
        "ready": "Pronto",
        "asset_label": "Asset: {name}",
        "asset_error": "Errore caricamento: {name}",
        "asset_not_found": "Asset non trovato: {name}",
        "gui_not_available": "\n[GUI Companion] Tkinter non disponibile ({err}). Continuo solo su terminale.",
        
        # Esplorazione
        "explore_prompt": "\nDove vai? [{exits}] (i = inventario, save = salva, q = esci): ",
        "move_blocked": "Non puoi proseguire in quella direzione.",
        "not_in_explore": "Non sei in fase di esplorazione.",
        "moved_to": "Ti sei spostato verso: {area}",
        "entered": "Sei entrato in: {area}",
        
        # Combattimento
        "boss_warning_1": "!!!           ATTENZIONE: SCONTRO BOSS FINALE            !!!",
        "monster_bars_way": "\n!!! Un {monster} ti sbarra la strada !!!",
        "wild_monster_appears": "Un {monster} selvatico appare!",
        "combat_prompt": "\n[a] Attacca  [s] {skill} ({cost} {resource})  [o] Oggetto  [f] Fuggi  [i] Inventario: ",
        "hit_monster": "Colpisci {monster}: {damage} danni.{extra}",
        "fatigued_hit": "Sferri un Colpo Affaticato a {monster}: {damage} danni.{extra}",
        "monster_hits_you": "{monster} ti colpisce: {damage} danni.{extra}",
        "bulwark_reflects": "Il Baluardo riflette {damage} danni!",
        "bulwark_reflects_log": "Il Baluardo Difensivo riflette {damage} danni su {monster}!",
        "boss_unleashes": "{monster} scatena {skill}! {damage} DANNI DEVASTANTI!",
        "boss_unleashes_log": "{monster} scatena {skill}! Infligge {damage} danni travolgenti a {player}!",
        "boss_phase_2": "!!! {monster} entra nella FASE 2: Furia Draconica! Il suo potere distruttivo aumenta! !!!",
        "skill_used": "{skill}! {detail} (-{cost} {resource})",
        "skill_damage": "{damage} danni",
        "skill_pure_damage": "{damage} danni puri",
        "skill_healed": "{hp} HP recuperati",
        "skill_buff": "{buff} attivo per {turns} turni",
        "insufficient_resource": "{resource} insufficiente per usare {skill} (richiesti {cost}).",
        "flee_success": "\nSei riuscito a fuggire!",
        "flee_success_log": "{player} e' fuggito dal combattimento.",
        "flee_failed": "Non riesci a fuggire!",
        "player_defeated": "{player} e' stato sconfitto...",
        "game_over": "\n### SEI STATO SCONFITTO - GAME OVER ###",
        "monster_defeated": "*** {monster} sconfitto! ***  +{exp} EXP, +{gold} oro",
        "monster_defeated_log": "{monster} e' stato sconfitto!",
        "loot_obtained": "Bottino: {item} ({rarity})",
        "loot_obtained_log": "Hai ottenuto: {item} ({rarity})",
        "inventory_full_loot_lost": "[!] Inventario pieno ({max}/{max}): {item} ({rarity}) lasciato a terra!",
        "inventory_full_loot_lost_log": "Inventario pieno: {item} lasciato a terra.",
        "level_up_notice": "LEVEL UP! Livello {level}: HP max {hp_max}, ATT {att}, DIF {dif}, {res_name} max {res_max}",
        "started_new_game_log": "Nuova partita iniziata per {player} ({classe}).",
        "hit_monster_log": "{player} infligge {damage} danni a {monster}.",
        "fatigued_hit_log": "{player} e' esausto e sferra un Colpo Affaticato per {damage} danni a {monster}!",
        "monster_hits_player_log": "{monster} infligge {damage} danni a {player}.",
        "skill_strike_log": "{player} scatena {skill}: {damage} danni a {monster}!",
        "skill_pure_log": "{player} scaglia {skill}: {damage} danni puri a {monster}!",
        "skill_buff_log": "{player} attiva {skill}: difesa aumentata per {turns} turni!",
        "skill_heal_log": "{player} usa {skill} e recupera {hp} HP.",
        "epic_triumph_log": "VITTORIA EPICA: Il Boss Finale e' stato abbattuto!",
        "equipped_log": "{player} ha equipaggiato {item} nello slot {slot}.",
        "unequipped_log": "{player} ha disequipaggiato {item} dallo slot {slot}.",
        "resource_gain_tag": "+{amount} risorsa",
        "resource_cost_tag": "-{amount} risorsa",
        
        # Vittoria Finale
        "victory_banner_title": "***       TRIONFO EPICO: IL BOSS FINALE E' STATO ABBATTUTO!     ***",
        "victory_boss_fallen": "\n  Il temibile {monster} e' caduto al suolo!",
        "victory_rewards": "  Hai ottenuto +{exp} EXP e +{gold} oro.",
        "victory_legendary_loot": "  Bottino leggendario: {item} ({rarity})",
        "endgame_stats_title": "STATISTICHE DI FINE PARTITA",
        "stat_hero": "Eroe:",
        "stat_level": "Livello raggiunto:",
        "stat_gold": "Oro accumulato:",
        "stat_monsters_slain": "Mostri sconfitti:",
        "stat_combat_turns": "Turni combattuti:",
        "stat_remaining_hp": "Salute residua:",
        "victory_legend": "\nComplimenti! Hai liberato il dungeon e scritto il tuo nome nella leggenda!\n",
        "play_again_prompt": "\nDesideri iniziare una nuova partita o uscire? [1 = nuova partita, q = esci]: ",
        "thanks_playing": "\nGrazie per aver giocato! Gloria al vincitore!",
        
        # Inventario ed Equipaggiamento
        "inv_title": "\n--- INVENTARIO (Zaino: {used}/{max} slot) ---",
        "inv_closed": "\nInventario chiuso.",
        "backpack_equip_title": "\n=== ZAINO E EQUIPAGGIAMENTO (Zaino: {used}/{max} slot) ===",
        "active_weapon": "Arma attiva:",
        "active_armor": "Armatura attiva:",
        "items_in_backpack": "Oggetti nello zaino:",
        "none": "(nessuna)",
        "empty": "(vuoto)",
        "backpack_actions": "\nAzioni zaino (Zaino: {used}/{max} slot):\n  [e] Equipaggia  [d] Disequipaggia  [s] Scarta  [0/q] Torna indietro: ",
        "backpack_empty_equip": "\n! Lo zaino e' vuoto, nessun oggetto da equipaggiare.",
        "backpack_empty_discard": "\n! Lo zaino e' vuoto, nessun oggetto da scartare.",
        "equip_prompt": "Numero oggetto da equipaggiare (0 = annulla): ",
        "not_equippable": "\n! {item} non e' equipaggiabile (tipo: {type}).",
        "equipped_msg": "\nEquipaggiato: {item}",
        "swapped_msg": " (Riposto nell'inventario: {item})",
        "no_active_equip": "\n! Nessun equipaggiamento attivo da disequipaggiare.",
        "inventory_full_unequip": "\n! Inventario pieno ({used}/{max}): libera spazio nello zaino prima di disequipaggiare.",
        "active_slots_title": "\nSlot attivi:",
        "slot_weapon_label": "[1/arma]     Arma ({item})",
        "slot_armor_label": "[2/armatura] Armatura ({item})",
        "unequip_prompt": "Quale slot disequipaggiare? (0 = annulla): ",
        "discard_prompt": "Numero oggetto da scartare (0 = annulla): ",
        "discard_confirm": "Confermi di voler buttare via '{item}'? [s/n]: ",
        "discarded_msg": "\nHai scartato: {item}.",
        "discarded_log": "{player} ha gettato via {item}.",
        "item_not_usable": "{item} non e' utilizzabile.",
        "no_usable_consumables": "\n! Nessun consumabile utilizzabile.",
        "use_item_prompt": "Oggetto (0 = annulla): ",
        "used_item_log": "{player} usa {item} e recupera {hp} HP.",
        "used_item_res_log": "{player} recupera {amount} {resource}.",
        "used_item_cli": "Usi {item}: {recovery}.",
        "no_effect": "nessun effetto",
        "unequipped_success": "Hai disequipaggiato {item} dallo slot {slot}.",
        "slot_invalid": "Slot '{slot}' non valido (scegli 'arma' o 'armatura').",
        "slot_empty": "Nessun equipaggiamento nello slot {slot}.",
        
        # Salvataggio e Caricamento
        "save_success": "Partita salvata con successo!",
        "load_success": "Partita caricata con successo!",
        "welcome_back": "Partita caricata: bentornato {player}!",
        "save_not_found": "File di salvataggio '{file}' non trovato.",
        "save_error": "Impossibile salvare la partita: {err}",
        "load_error": "Errore durante il caricamento del salvataggio: {err}",
        "no_active_game_to_save": "Nessuna partita attiva da salvare.",
        
        # Demo Bot
        "demo_triumph": "\n*** Conclusione trionfale della modalita' Demo: Boss sconfitto! ***\n",
        "demo_end": "\n--- Fine demo. Ultimi messaggi di log ---",
    },
    
    "en": {
        # Main Menu & Startup
        "game_title": "=== DUNGIASI RPG ===",
        "menu_new_game": "[1] New Game",
        "menu_load_game": "[2] Load Game",
        "menu_quit": "[q] Quit",
        "choice_prompt": "Choice: ",
        "invalid_choice": "Invalid choice. Options: {options}",
        "farewell": "\nFarewell, adventurer!",
        "hero_name_prompt": "\nHero name: ",
        "default_hero_name": "Hero",
        "starting_new_game": "Starting a new game...",
        "select_class_title": "\nChoose your class:",
        "class_prompt": "Class (number): ",
        "select_zone_title": "\nAvailable zones:",
        "zone_prompt": "Zone (number): ",
        
        # State UI
        "backpack_slot": "Backpack {used}/{max} slots",
        "backpack_stats": "Backpack: {used}/{max} slots",
        "stats_hp": "HP",
        "active_effects": "Effects: {effects}",
        "turns_suffix": "{count} turns",
        "exits": "Exits:",
        "asset_viewer_title": "Dungiasi RPG - Asset Viewer",
        "waiting_event": "(Waiting for first game event...)",
        "ready": "Ready",
        "asset_label": "Asset: {name}",
        "asset_error": "Failed to load: {name}",
        "asset_not_found": "Asset not found: {name}",
        "gui_not_available": "\n[GUI Companion] Tkinter not available ({err}). Continuing in terminal mode.",
        
        # Exploration
        "explore_prompt": "\nWhere to? [{exits}] (i = inventory, save = save, q = quit): ",
        "move_blocked": "You cannot go in that direction.",
        "not_in_explore": "You are not in exploration mode.",
        "moved_to": "You moved towards: {area}",
        "entered": "You entered: {area}",
        
        # Combat
        "boss_warning_1": "!!!              WARNING: FINAL BOSS BATTLE             !!!",
        "monster_bars_way": "\n!!! A {monster} blocks your path !!!",
        "wild_monster_appears": "A wild {monster} appears!",
        "combat_prompt": "\n[a] Attack  [s] {skill} ({cost} {resource})  [o] Item  [f] Flee  [i] Inventory: ",
        "hit_monster": "You strike {monster}: {damage} damage.{extra}",
        "fatigued_hit": "You deliver an Exhausted Strike to {monster}: {damage} damage.{extra}",
        "monster_hits_you": "{monster} strikes you: {damage} damage.{extra}",
        "bulwark_reflects": "Defensive Bulwark reflects {damage} damage!",
        "bulwark_reflects_log": "Defensive Bulwark reflects {damage} damage onto {monster}!",
        "boss_unleashes": "{monster} unleashes {skill}! {damage} DEVASTATING DAMAGE!",
        "boss_unleashes_log": "{monster} unleashes {skill}! Deals {damage} crushing damage to {player}!",
        "boss_phase_2": "!!! {monster} enters PHASE 2: Draconic Fury! Its destructive power surges! !!!",
        "skill_used": "{skill}! {detail} (-{cost} {resource})",
        "skill_damage": "{damage} damage",
        "skill_pure_damage": "{damage} pure damage",
        "skill_healed": "{hp} HP restored",
        "skill_buff": "{buff} active for {turns} turns",
        "insufficient_resource": "Not enough {resource} to use {skill} (requires {cost}).",
        "flee_success": "\nYou managed to escape!",
        "flee_success_log": "{player} fled from combat.",
        "flee_failed": "You failed to escape!",
        "player_defeated": "{player} has been defeated...",
        "game_over": "\n### YOU HAVE BEEN DEFEATED - GAME OVER ###",
        "monster_defeated": "*** {monster} defeated! ***  +{exp} EXP, +{gold} gold",
        "monster_defeated_log": "{monster} was defeated!",
        "loot_obtained": "Loot: {item} ({rarity})",
        "loot_obtained_log": "You obtained: {item} ({rarity})",
        "inventory_full_loot_lost": "[!] Inventory full ({max}/{max}): {item} ({rarity}) left behind!",
        "inventory_full_loot_lost_log": "Inventory full: {item} left behind.",
        "level_up_notice": "LEVEL UP! Level {level}: Max HP {hp_max}, ATK {att}, DEF {dif}, Max {res_name} {res_max}",
        "started_new_game_log": "New game started for {player} ({classe}).",
        "hit_monster_log": "{player} deals {damage} damage to {monster}.",
        "fatigued_hit_log": "{player} is exhausted and strikes a Fatigued Blow for {damage} damage to {monster}!",
        "monster_hits_player_log": "{monster} deals {damage} damage to {player}.",
        "skill_strike_log": "{player} unleashes {skill}: {damage} damage to {monster}!",
        "skill_pure_log": "{player} casts {skill}: {damage} pure damage to {monster}!",
        "skill_buff_log": "{player} activates {skill}: defense increased for {turns} turns!",
        "skill_heal_log": "{player} uses {skill} and restores {hp} HP.",
        "epic_triumph_log": "EPIC TRIUMPH: The Final Boss has been slain!",
        "equipped_log": "{player} equipped {item} in slot {slot}.",
        "unequipped_log": "{player} unequipped {item} from slot {slot}.",
        "resource_gain_tag": "+{amount} resource",
        "resource_cost_tag": "-{amount} resource",
        
        # Victory
        "victory_banner_title": "***        EPIC TRIUMPH: THE FINAL BOSS HAS BEEN SLAIN!     ***",
        "victory_boss_fallen": "\n  The dreaded {monster} has collapsed to the ground!",
        "victory_rewards": "  You obtained +{exp} EXP and +{gold} gold.",
        "victory_legendary_loot": "  Legendary loot: {item} ({rarity})",
        "endgame_stats_title": "FINAL GAME STATISTICS",
        "stat_hero": "Hero:",
        "stat_level": "Level reached:",
        "stat_gold": "Gold accumulated:",
        "stat_monsters_slain": "Monsters slain:",
        "stat_combat_turns": "Turns fought:",
        "stat_remaining_hp": "Remaining health:",
        "victory_legend": "\nCongratulations! You cleared the dungeon and etched your name in legend!\n",
        "play_again_prompt": "\nWould you like to start a new game or quit? [1 = new game, q = quit]: ",
        "thanks_playing": "\nThank you for playing! Glory to the victor!",
        
        # Inventory & Equipment
        "inv_title": "\n--- INVENTORY (Backpack: {used}/{max} slots) ---",
        "inv_closed": "\nInventory closed.",
        "backpack_equip_title": "\n=== BACKPACK AND EQUIPMENT (Backpack: {used}/{max} slots) ===",
        "active_weapon": "Active weapon:",
        "active_armor": "Active armor:",
        "items_in_backpack": "Items in backpack:",
        "none": "(none)",
        "empty": "(empty)",
        "backpack_actions": "\nBackpack actions (Backpack: {used}/{max} slots):\n  [e] Equip  [d] Unequip  [s] Discard  [0/q] Go back: ",
        "backpack_empty_equip": "\n! The backpack is empty, no items to equip.",
        "backpack_empty_discard": "\n! The backpack is empty, no items to discard.",
        "equip_prompt": "Item number to equip (0 = cancel): ",
        "not_equippable": "\n! {item} is not equippable (type: {type}).",
        "equipped_msg": "\nEquipped: {item}",
        "swapped_msg": " (Returned to backpack: {item})",
        "no_active_equip": "\n! No active equipment to unequip.",
        "inventory_full_unequip": "\n! Inventory full ({used}/{max}): free space in backpack before unequipping.",
        "active_slots_title": "\nActive slots:",
        "slot_weapon_label": "[1/weapon] Weapon ({item})",
        "slot_armor_label": "[2/armor]  Armor ({item})",
        "unequip_prompt": "Which slot to unequip? (0 = cancel): ",
        "discard_prompt": "Item number to discard (0 = cancel): ",
        "discard_confirm": "Are you sure you want to discard '{item}'? [y/n]: ",
        "discarded_msg": "\nYou discarded: {item}.",
        "discarded_log": "{player} discarded {item}.",
        "item_not_usable": "{item} cannot be used.",
        "no_usable_consumables": "\n! No usable consumables.",
        "use_item_prompt": "Item (0 = cancel): ",
        "used_item_log": "{player} uses {item} and restores {hp} HP.",
        "used_item_res_log": "{player} restores {amount} {resource}.",
        "used_item_cli": "You use {item}: {recovery}.",
        "no_effect": "no effect",
        "unequipped_success": "You unequipped {item} from slot {slot}.",
        "slot_invalid": "Slot '{slot}' is invalid (choose 'weapon' or 'armor').",
        "slot_empty": "No equipment in slot {slot}.",
        
        # Save & Load
        "save_success": "Game saved successfully!",
        "load_success": "Game loaded successfully!",
        "welcome_back": "Game loaded: welcome back {player}!",
        "save_not_found": "Save file '{file}' not found.",
        "save_error": "Could not save the game: {err}",
        "load_error": "Error while loading save file: {err}",
        "no_active_game_to_save": "No active game to save.",
        
        # Demo Bot
        "demo_triumph": "\n*** Triumphant conclusion of Demo mode: Final Boss defeated! ***\n",
        "demo_end": "\n--- End of demo. Recent log messages ---",
    },
}


def t(key: str, lang: Optional[str] = None, **kwargs: Any) -> str:
    """Restituisce la stringa tradotta per la chiave specificata."""
    chosen_lang = lang if lang is not None else _CURRENT_LANG
    table = TEXTS.get(chosen_lang, TEXTS["it"])
    template = table.get(key, TEXTS["it"].get(key, key))
    if kwargs:
        try:
            return template.format(**kwargs)
        except Exception:
            return template
    return template


# =====================================================================
# TRADUZIONI ENTITÀ DI GIOCO (CLASSI, ABILITÀ, OGGETTI, MOSTRI, AREE)
# =====================================================================

CLASS_TRANSLATIONS: Dict[PlayerClass, Dict[str, Dict[str, str]]] = {
    PlayerClass.GUERRIERO: {
        "it": {
            "name": "Guerriero",
            "ability_name": "Colpo Devastante",
            "ability_desc": "Un fendente carico di rabbia: infligge Attacco*1.8 mitigato solo dal 70% della difesa nemica. Costa 40 Furia.",
        },
        "en": {
            "name": "Warrior",
            "ability_name": "Devastating Strike",
            "ability_desc": "A rage-infused strike: deals Attack*1.8 mitigated by only 70% of enemy defense. Costs 40 Fury.",
        },
    },
    PlayerClass.MAGO: {
        "it": {
            "name": "Mago",
            "ability_name": "Dardo Arcano",
            "ability_desc": "Un dardo di energia pura che infligge Attacco*1.4 ignorando totalmente la difesa nemica. Costa 15 Mana.",
        },
        "en": {
            "name": "Mage",
            "ability_name": "Arcane Bolt",
            "ability_desc": "A bolt of pure arcane energy that deals Attack*1.4 completely ignoring enemy defense. Costs 15 Mana.",
        },
    },
    PlayerClass.CAVALIERE: {
        "it": {
            "name": "Cavaliere",
            "ability_name": "Baluardo Difensivo",
            "ability_desc": "Alza lo scudo per 2 turni: +50% difesa e ogni colpo subito viene parzialmente riflesso al nemico. Costa 35 Stamina.",
        },
        "en": {
            "name": "Knight",
            "ability_name": "Defensive Bulwark",
            "ability_desc": "Raises shield for 2 turns: +50% defense and 25% of damage taken is reflected back to the enemy. Costs 35 Stamina.",
        },
    },
    PlayerClass.MEDICO: {
        "it": {
            "name": "Medico",
            "ability_name": "Pronto Soccorso",
            "ability_desc": "Cura istantaneamente il 35% degli HP Max del giocatore. Costa 12 Mana.",
        },
        "en": {
            "name": "Cleric",
            "ability_name": "First Aid",
            "ability_desc": "Instantly heals 35% of the player's Max HP. Costs 12 Mana.",
        },
    },
}

RESOURCE_TRANSLATIONS: Dict[ResourceType, Dict[str, str]] = {
    ResourceType.FURIA: {"it": "Furia", "en": "Fury"},
    ResourceType.MANA: {"it": "Mana", "en": "Mana"},
    ResourceType.STAMINA: {"it": "Stamina", "en": "Stamina"},
}

RARITY_TRANSLATIONS: Dict[Rarity, Dict[str, str]] = {
    Rarity.COMUNE: {"it": "Comune", "en": "Common"},
    Rarity.RARO: {"it": "Raro", "en": "Rare"},
    Rarity.LEGGENDARIO: {"it": "Leggendario", "en": "Legendary"},
}

ITEM_TYPE_TRANSLATIONS: Dict[ItemType, Dict[str, str]] = {
    ItemType.ARMA: {"it": "Arma", "en": "Weapon"},
    ItemType.ARMATURA: {"it": "Armatura", "en": "Armor"},
    ItemType.CONSUMABILE: {"it": "Consumabile", "en": "Consumable"},
    ItemType.VARIE: {"it": "Varie", "en": "Misc"},
}

DIRECTION_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "N": {"it": "N", "en": "N"},
    "S": {"it": "S", "en": "S"},
    "E": {"it": "E", "en": "E"},
    "O": {"it": "O", "en": "W"},
}

ITEM_DATA: Dict[str, Dict[str, Dict[str, str]]] = {
    "spada_ferro": {
        "it": {"nome": "Spada di Ferro", "desc": "Una solida lama di ferro a un filo."},
        "en": {"nome": "Iron Sword", "desc": "A solid single-edged iron blade."},
    },
    "spadone_due_mani": {
        "it": {"nome": "Spadone a Due Mani", "desc": "Pesante e devastante, ideale per il Guerriero."},
        "en": {"nome": "Two-Handed Greatsword", "desc": "Heavy and devastating, ideal for the Warrior."},
    },
    "bastone_legno": {
        "it": {"nome": "Bastone di Frassino", "desc": "Canalizza debolmente l'energia magica."},
        "en": {"nome": "Ash Staff", "desc": "Faintly channels magical energy."},
    },
    "bastone_arcano": {
        "it": {"nome": "Bastone delle Maree Arcane", "desc": "Un cristallo brillante amplifica i dardi arcani."},
        "en": {"nome": "Staff of Arcane Tides", "desc": "A glowing crystal amplifies arcane bolts."},
    },
    "tomo_preghiere": {
        "it": {"nome": "Tomo dei Riti Curativi", "desc": "Pagine intrise di formule di soccorso."},
        "en": {"nome": "Tome of Healing Rites", "desc": "Pages imbued with soothing incantations."},
    },
    "tomo_santificato": {
        "it": {"nome": "Codice della Grazia Divina", "desc": "Emana calore sacro respingendo le tenebre."},
        "en": {"nome": "Codex of Divine Grace", "desc": "Radiates holy warmth, warding off darkness."},
    },
    "lancia_guardia": {
        "it": {"nome": "Lancia della Guardia", "desc": "Asta bilanciata per colpire mantenendo la guardia."},
        "en": {"nome": "Guard's Spear", "desc": "Balanced spear to strike while maintaining guard."},
    },
    "pugnale_acciaio": {
        "it": {"nome": "Pugnale d'Acciaio", "desc": "Leggero e maneggevole."},
        "en": {"nome": "Steel Dagger", "desc": "Light and nimble."},
    },
    "veste_magica": {
        "it": {"nome": "Tunica del Novizio", "desc": "Tessuto leggero che non ostacola la concentrazione."},
        "en": {"nome": "Novice's Tunic", "desc": "Light fabric that does not hinder concentration."},
    },
    "veste_runica": {
        "it": {"nome": "Veste Tessuta di Rune", "desc": "Simboli protettivi contro incantesimi."},
        "en": {"nome": "Rune-Woven Robe", "desc": "Protective glyphs warding against spells."},
    },
    "armatura_cuoio": {
        "it": {"nome": "Armatura di Cuoio Indurito", "desc": "Protegge dagli artigli senza limitare la mobilita'."},
        "en": {"nome": "Hardened Leather Armor", "desc": "Protects against claws without hindering mobility."},
    },
    "scudo_legno": {
        "it": {"nome": "Scudo di Legno Rinforzato", "desc": "Asce e denti faticano a penetrare le sue assi."},
        "en": {"nome": "Reinforced Wooden Shield", "desc": "Axes and fangs struggle to pierce its planks."},
    },
    "scudo_runico": {
        "it": {"nome": "Scudo a Torre Runico", "desc": "Una fortezza portatile ideale per sostenere il Baluardo."},
        "en": {"nome": "Runic Tower Shield", "desc": "A portable fortress ideal for sustaining the Bulwark."},
    },
    "corazza_piastre": {
        "it": {"nome": "Corazza di Piastre Forgiata", "desc": "Acciaio temprato che attutisce i colpi violenti."},
        "en": {"nome": "Forged Plate Armor", "desc": "Tempered steel that dampens heavy blows."},
    },
    "pozione_cura": {
        "it": {"nome": "Pozione Curativa", "desc": "Ripristina 25 punti ferita."},
        "en": {"nome": "Healing Potion", "desc": "Restores 25 Health Points."},
    },
    "pozione_mana": {
        "it": {"nome": "Elisir di Mana", "desc": "Ricarica 25 punti Mana."},
        "en": {"nome": "Mana Elixir", "desc": "Restores 25 Mana points."},
    },
    "pozione_stamina": {
        "it": {"nome": "Tonico del Vigore", "desc": "Recupera 35 punti Stamina."},
        "en": {"nome": "Vigor Tonic", "desc": "Restores 35 Stamina points."},
    },
    "amuleto_drago": {
        "it": {"nome": "Amuleto del Drago Ancestrale", "desc": "Brilla di una luce rossa eterna, reliquia delle profondita'."},
        "en": {"nome": "Amulet of the Ancient Dragon", "desc": "Glows with an eternal crimson light, relic of the deep."},
    },
}

MONSTER_DATA: Dict[str, Dict[str, Dict[str, str]]] = {
    "pipistrello": {
        "it": {"nome": "Pipistrello Gigante"},
        "en": {"nome": "Giant Bat"},
    },
    "goblin": {
        "it": {"nome": "Goblin Esploratore"},
        "en": {"nome": "Goblin Scout"},
    },
    "ragno": {
        "it": {"nome": "Ragno Velenoso"},
        "en": {"nome": "Poisonous Spider"},
    },
    "scheletro": {
        "it": {"nome": "Guardiano Scheletrico"},
        "en": {"nome": "Skeletal Guardian"},
    },
    "orco": {
        "it": {"nome": "Orco Guerriero"},
        "en": {"nome": "Orc Warrior"},
    },
    "spettro": {
        "it": {"nome": "Spettro Tormentato"},
        "en": {"nome": "Tormented Wraith"},
    },
    "golem": {
        "it": {"nome": "Golem di Pietra"},
        "en": {"nome": "Stone Golem"},
    },
    "drago": {
        "it": {"nome": "Drago Ancestrale", "abilita_boss": "Soffio Infernale"},
        "en": {"nome": "Ancient Dragon", "abilita_boss": "Infernal Breath"},
    },
}

AREA_DATA: Dict[str, Dict[str, Dict[str, str]]] = {
    "ingresso": {
        "it": {
            "nome": "Ingresso del Dungeon",
            "desc": "Un massiccio cancello di pietra logorato dai secoli. Verso nord le tenebre si infittiscono.",
        },
        "en": {
            "nome": "Dungeon Entrance",
            "desc": "A massive stone gate weathered by centuries. Darkness thickens to the north.",
        },
    },
    "atrio": {
        "it": {
            "nome": "Atrio dei Bivi",
            "desc": "Un'ampia sala circolare con colonne spezzate. Cunicoli scavati nella roccia si diramano a est e ovest.",
        },
        "en": {
            "nome": "Crossroads Atrium",
            "desc": "A vast circular hall with broken pillars. Passages carved in rock branch east and west.",
        },
    },
    "caverne": {
        "it": {
            "nome": "Caverne Umide",
            "desc": "Stalattiti gocciolano dal soffitto. L'aria odora di terra umida e muschio fungino.",
        },
        "en": {
            "nome": "Damp Caverns",
            "desc": "Stalactites drip from the ceiling. The air smells of wet earth and fungal moss.",
        },
    },
    "nido_ragni": {
        "it": {
            "nome": "Nido dei Ragni",
            "desc": "Fitte ragnatele bianche ricoprono pareti e vecchi resti di scheletri appesi.",
        },
        "en": {
            "nome": "Spider's Nest",
            "desc": "Thick white webs blanket walls and old hanging skeletal remains.",
        },
    },
    "cripta": {
        "it": {
            "nome": "Cripta Dimenticata",
            "desc": "Sarcofagi aperti e polvere d'ossa. Una brezza gelida spegne quasi il chiarore delle torce.",
        },
        "en": {
            "nome": "Forgotten Crypt",
            "desc": "Open sarcophagi and bone dust. A chilling draught nearly snuffs out torchlight.",
        },
    },
    "catacombe": {
        "it": {
            "nome": "Catacombe Profonde",
            "desc": "Loculi scavati nel tufo su ogni parete. Si sentono lamenti soffusi in lontananza.",
        },
        "en": {
            "nome": "Deep Catacombs",
            "desc": "Burial niches carved into tufa on every wall. Faint wails echo in the distance.",
        },
    },
    "sala_guardie": {
        "it": {
            "nome": "Sala delle Guardie",
            "desc": "Tavolacci ribaltati e scudi spezzati testimoniano un'antica guarnigione caduta in battaglia.",
        },
        "en": {
            "nome": "Guard Hall",
            "desc": "Overturned tables and shattered shields testify to an ancient garrison fallen in battle.",
        },
    },
    "corridoio_runico": {
        "it": {
            "nome": "Corridoio delle Rune",
            "desc": "Pietre megalitiche incise di glifi luminosi. L'accesso alle profondita' e' difeso da colossi di pietra.",
        },
        "en": {
            "nome": "Runic Corridor",
            "desc": "Megalithic stones engraved with glowing glyphs. The path to the deep is guarded by stone colossi.",
        },
    },
    "sala_trono": {
        "it": {
            "nome": "Sala del Trono Ancestrale",
            "desc": "Un'immensa caverna con un trono dorato in rovina. Un colossale drago dorme circondato da tesori.",
        },
        "en": {
            "nome": "Ancestral Throne Room",
            "desc": "An immense cavern with a ruined golden throne. A colossal dragon slumbers surrounded by treasures.",
        },
    },
}


def get_class_name(c: PlayerClass, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return CLASS_TRANSLATIONS.get(c, {}).get(l, {}).get("name", c.value)


def get_class_ability_name(c: PlayerClass, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return CLASS_TRANSLATIONS.get(c, {}).get(l, {}).get("ability_name", "")


def get_class_ability_desc(c: PlayerClass, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return CLASS_TRANSLATIONS.get(c, {}).get(l, {}).get("ability_desc", "")


def get_resource_name(r: ResourceType, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return RESOURCE_TRANSLATIONS.get(r, {}).get(l, r.value)


def get_rarity_name(r: Rarity, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return RARITY_TRANSLATIONS.get(r, {}).get(l, r.value)


def get_item_type_name(it: ItemType, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return ITEM_TYPE_TRANSLATIONS.get(it, {}).get(l, it.value)


def get_direction_label(d_code: str, lang: Optional[str] = None) -> str:
    l = lang or _CURRENT_LANG
    return DIRECTION_TRANSLATIONS.get(d_code.upper(), {}).get(l, d_code)
