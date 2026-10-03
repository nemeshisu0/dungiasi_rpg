"""
main.py
=======
Frontend CLI di Dungiasi RPG: unico modulo con print()/input().
Include hook per visualizzazione sprite tramite tool CLI (chafa/kitty) o fallback,
e supporto completo alla localizzazione multilingua (Italiano / English).
"""

from __future__ import annotations

import argparse
import os
import queue
import random
import shutil
import subprocess
import sys
import threading
from typing import Any, Dict, List, Optional

from config import (
    CHAFA_ARGS_KITTY,
    CHAFA_ARGS_PIXEL_ART,
    CLASS_PROFILES,
    GUI_WINDOW_SIZE,
    GUI_WINDOW_TITLE,
    CombatAction,
    Direction,
    GameState,
    ItemType,
    PlayerClass,
)
from engine import GameEngine
from i18n import (
    get_class_ability_desc,
    get_class_ability_name,
    get_class_name,
    get_direction_label,
    get_item_type_name,
    get_language,
    get_rarity_name,
    get_resource_name,
    set_language,
    t,
)
from world import popola_mondo

LARGHEZZA_BARRA = 20
PASSI_DEMO = 60

DIR_MAP: Dict[str, Direction] = {
    "n": Direction.NORD,
    "s": Direction.SUD,
    "e": Direction.EST,
    "o": Direction.OVEST,
    "w": Direction.OVEST,
}


# =====================================================================
# SELEZIONE LINGUA INTERATTIVA
# =====================================================================

def seleziona_lingua_interattiva() -> str:
    """Mostra la schermata iniziale per la scelta della lingua."""
    print("\n===============================================")
    print("  🌐 Select Language / Seleziona Lingua")
    print("===============================================")
    print("  [1] Italiano (Italian)")
    print("  [2] English (Inglese)")
    print("-----------------------------------------------")
    while True:
        try:
            scelta = input("Choice / Scelta [1/2]: ").strip()
        except EOFError:
            raise SystemExit(0)
        if scelta in ("1", "it", "italiano"):
            set_language("it")
            return "it"
        elif scelta in ("2", "en", "english", "inglese"):
            set_language("en")
            return "en"
        print("  Invalid option / Opzione non valida. Enter 1 or 2.")


# =====================================================================
# RENDERING GRAFICO E TESTUALE (CLI + COMPANION GUI)
# =====================================================================

_gui_queue: Optional[queue.Queue[str]] = None
_gui_thread: Optional[threading.Thread] = None


def _gui_worker(gui_q: queue.Queue[str], titolo: str, dimensioni: str) -> None:
    """Loop della finestra Tkinter in background (thread daemon)."""
    try:
        import tkinter as tk
    except Exception as exc:
        print(t("gui_not_available", err=exc))
        return

    try:
        root = tk.Tk()
        root.title(titolo)
        root.geometry(dimensioni)
        root.resizable(True, True)

        header = tk.Label(root, text=titolo, font=("Helvetica", 11, "bold"))
        header.pack(pady=6)

        img_label = tk.Label(root, text=t("waiting_event"))
        img_label.pack(expand=True, fill="both", padx=10, pady=10)

        status_label = tk.Label(root, text=t("ready"), font=("Helvetica", 9, "italic"))
        status_label.pack(pady=4)

        img_ref: Dict[str, Any] = {"img": None}

        def process_queue() -> None:
            try:
                while not gui_q.empty():
                    sprite_path = gui_q.get_nowait()
                    if sprite_path and os.path.exists(sprite_path):
                        try:
                            photo = tk.PhotoImage(file=sprite_path)
                            img_label.config(image=photo, text="")
                            img_ref["img"] = photo
                            status_label.config(text=t("asset_label", name=os.path.basename(sprite_path)))
                        except Exception:
                            status_label.config(text=t("asset_error", name=os.path.basename(sprite_path)))
                    elif sprite_path:
                        status_label.config(text=t("asset_not_found", name=os.path.basename(sprite_path)))
            except Exception:
                pass
            root.after(100, process_queue)

        root.after(100, process_queue)
        root.mainloop()
    except Exception as exc:
        print(t("gui_not_available", err=exc))


def avvia_gui_companion(titolo: Optional[str] = None, dimensioni: str = GUI_WINDOW_SIZE) -> bool:
    """Avvia la finestra companion in un thread daemon separato."""
    global _gui_queue, _gui_thread
    titolo_finestra = titolo or t("asset_viewer_title")
    try:
        import tkinter  # verifica preventiva rapida
    except Exception as exc:
        print(t("gui_not_available", err=exc))
        return False

    _gui_queue = queue.Queue()
    _gui_thread = threading.Thread(
        target=_gui_worker,
        args=(_gui_queue, titolo_finestra, dimensioni),
        daemon=True,
    )
    _gui_thread.start()
    return True


def aggiorna_gui_sprite(sprite_path: str) -> None:
    """Notifica la finestra GUI per visualizzare l'asset specificato."""
    if _gui_queue is not None:
        try:
            _gui_queue.put_nowait(sprite_path)
        except Exception:
            pass


def mostra_sprite(sprite_path: str) -> None:
    """Mostra lo sprite PNG nel terminale usando Chafa (pixel art o protocollo Kitty)
    e aggiorna la companion GUI se attiva; altrimenti mostra il fallback testuale.
    """
    aggiorna_gui_sprite(sprite_path)

    if os.path.exists(sprite_path):
        is_kitty = (
            "kitty" in os.environ.get("TERM", "").lower()
            or bool(os.environ.get("KITTY_WINDOW_ID"))
        )

        if shutil.which("chafa"):
            if is_kitty:
                try:
                    res = subprocess.run(
                        ["chafa"] + CHAFA_ARGS_KITTY + [sprite_path],
                        check=False,
                    )
                    if res.returncode == 0:
                        return
                except Exception:
                    pass

            try:
                res = subprocess.run(
                    ["chafa"] + CHAFA_ARGS_PIXEL_ART + [sprite_path],
                    check=False,
                )
                if res.returncode == 0:
                    return
            except Exception:
                pass

        if is_kitty and shutil.which("kitty"):
            try:
                res = subprocess.run(
                    ["kitty", "+kitten", "icat", sprite_path],
                    check=False,
                )
                if res.returncode == 0:
                    return
            except Exception:
                pass

    print(f"   [sprite: {sprite_path}]")


def barra(corrente: int, massimo: int) -> str:
    massimo = max(1, massimo)
    pieni = round(LARGHEZZA_BARRA * max(0, corrente) / massimo)
    return "[" + "#" * pieni + "-" * (LARGHEZZA_BARRA - pieni) + "]"


def mostra_stato_player(p: Dict[str, Any]) -> None:
    zaino_info = f"  {t('backpack_slot', used=p['inventario_occupato'], max=p['max_inventario'])}" if "max_inventario" in p else ""
    print(f"\n{p['nome']} ({p['classe']}) Lv.{p['livello']}  "
          f"EXP {p['exp']}/{p['exp_richiesta']}  Oro {p['oro']}{zaino_info}  "
          f"ATT {p['attacco']}  DIF {p['difesa']}")
    print(f"  {t('stats_hp'):<7} {barra(p['hp_corrente'], p['hp_max'])} {p['hp_corrente']}/{p['hp_max']}")
    print(f"  {p['risorsa_nome']:<7} {barra(p['risorsa_corrente'], p['risorsa_max'])} "
          f"{p['risorsa_corrente']}/{p['risorsa_max']}")
    if p.get("effetti_attivi"):
        effetti = ", ".join(f"{n} ({t('turns_suffix', count=turni)})" for n, turni in p["effetti_attivi"].items())
        print(f"  {t('active_effects', effects=effetti)}")


def mostra_mostro(m: Dict[str, Any]) -> None:
    print(f"\n  {m['nome']} (Lv.{m['livello']})  "
          f"{t('stats_hp')} {barra(m['hp_corrente'], m['hp_max'])} {m['hp_corrente']}/{m['hp_max']}")


def mostra_area(a: Dict[str, Any]) -> None:
    print(f"\n=== {a['nome']} ===")
    print(a["descrizione"])
    mostra_sprite(a["sprite_path"])
    print(f"{t('exits')} {', '.join(a['uscite_disponibili'])}")


def racconta_evento_turno(e: Dict[str, Any], nome_mostro: str) -> None:
    tipo = e["tipo"]
    if tipo == "attacco_player":
        extra = ""
        if e.get("risorsa_guadagnata"):
            extra = f" ({t('resource_gain_tag', amount=e['risorsa_guadagnata'])})"
        elif e.get("risorsa_consumata"):
            extra = f" ({t('resource_cost_tag', amount=e['risorsa_consumata'])})"
        if e.get("affaticato"):
            print(f"  {t('fatigued_hit', monster=nome_mostro, damage=e['danno'], extra=extra)}")
        else:
            print(f"  {t('hit_monster', monster=nome_mostro, damage=e['danno'], extra=extra)}")
    elif tipo == "abilita_speciale":
        if "danno" in e:
            dettaglio = t("skill_damage", damage=e["danno"])
        elif "hp_curati" in e:
            dettaglio = t("skill_healed", hp=e["hp_curati"])
        else:
            dettaglio = t("skill_buff", buff=e["buff_attivato"], turns=e["turni_buff"])
        print(f"  {t('skill_used', skill=e['nome_abilita'], detail=dettaglio, cost=e['risorsa_consumata'], resource=e['risorsa_nome'])}")
    elif tipo == "uso_oggetto":
        parti = []
        if e.get("hp_curati", 0) > 0:
            parti.append(f"+{e['hp_curati']} HP")
        if e.get("risorsa_curata", 0) > 0:
            parti.append(f"+{e['risorsa_curata']} {e['player']['risorsa_nome']}")
        recupero = ", ".join(parti) if parti else t("no_effect")
        print(f"  {t('used_item_cli', item=e['item']['nome'], recovery=recupero)}")
    elif tipo == "fuga_fallita":
        print(f"  {t('flee_failed')}")
    elif tipo == "attacco_mostro":
        extra = f" ({t('resource_gain_tag', amount=e['risorsa_guadagnata'])})" if e.get("risorsa_guadagnata") else ""
        print(f"  {t('monster_hits_you', monster=nome_mostro, damage=e['danno'], extra=extra)}")
        if e.get("contrattacco_baluardo"):
            print(f"  {t('bulwark_reflects', damage=e['contrattacco_baluardo'])}")
    elif tipo == "fase_boss":
        print(f"\n  >>> {e['messaggio']} <<<")
    elif tipo == "attacco_boss":
        print(f"  {t('boss_unleashes', monster=nome_mostro, skill=e['nome_abilita'], damage=e['danno'])}")


def render_evento(ev: Dict[str, Any], ctx: Dict[str, Any]) -> None:
    tipo = ev["tipo"]

    if tipo == "nuova_partita":
        mostra_stato_player(ev["player"])
    elif tipo in ("ingresso_area", "spostamento"):
        ctx["uscite"] = ev["area"]["uscite_disponibili"]
        mostra_area(ev["area"])
    elif tipo == "incontro":
        ctx["mostro"] = ev["mostro"]
        if ev["mostro"].get("is_boss"):
            print("\n" + "=" * 60)
            print(t("boss_warning_1"))
            print(f"!!!                 {ev['mostro']['nome'].upper()}                   !!!")
            print("=" * 60)
        else:
            print(t("monster_bars_way", monster=ev["mostro"]["nome"]))
        mostra_sprite(ev["mostro"]["sprite_path"])
        mostra_mostro(ev["mostro"])
    elif tipo == "turno_combattimento":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ctx["mostro"]["nome"])
        mostra_mostro(ev["mostro"])
        mostra_stato_player(ev["player"])
    elif tipo == "vittoria_finale":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ev["mostro_sconfitto"]["nome"])
        print("\n" + "*" * 64)
        print(t("victory_banner_title"))
        print("*" * 64)
        print(t("victory_boss_fallen", monster=ev["mostro_sconfitto"]["nome"]))
        print(t("victory_rewards", exp=ev["exp_ottenuta"], gold=ev["oro_ottenuto"]))
        for oggetto in ev["drop"]:
            print(t("victory_legendary_loot", item=oggetto["nome"], rarity=oggetto["rarita"]))
            mostra_sprite(oggetto["sprite_path"])
        for oggetto_perso in ev.get("drop_persi", []):
            print(f"  {t('inventory_full_loot_lost', item=oggetto_perso['nome'], rarity=oggetto_perso.get('rarita', ''), max=ev['player']['max_inventario'])}")

        st = ev.get("statistiche", {})
        print("\n" + "=" * 50)
        print(f"            {t('endgame_stats_title')}")
        print("=" * 50)
        print(f"  {t('stat_hero'):<22} {ev['player']['nome']} ({st.get('classe', ev['player']['classe'])})")
        print(f"  {t('stat_level'):<22} Lv.{st.get('livello_raggiunto', ev['player']['livello'])}")
        print(f"  {t('stat_gold'):<22} {st.get('oro_totale', ev['player']['oro'])}")
        print(f"  {t('stat_monsters_slain'):<22} {st.get('mostri_sconfitti', 0)}")
        print(f"  {t('stat_combat_turns'):<22} {st.get('turni_combattimento', 0)}")
        print(f"  {t('stat_remaining_hp'):<22} {st.get('hp_finali', '')}")
        print("=" * 50)
        print(t("victory_legend"))
        mostra_stato_player(ev["player"])
    elif tipo == "vittoria_combattimento":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ev["mostro_sconfitto"]["nome"])
        print(f"\n{t('monster_defeated', monster=ev['mostro_sconfitto']['nome'], exp=ev['exp_ottenuta'], gold=ev['oro_ottenuto'])}")
        for oggetto in ev["drop"]:
            print(f"  {t('loot_obtained', item=oggetto['nome'], rarity=oggetto['rarita'])}")
            mostra_sprite(oggetto["sprite_path"])
        for oggetto_perso in ev.get("drop_persi", []):
            print(f"  {t('inventory_full_loot_lost', item=oggetto_perso['nome'], rarity=oggetto_perso.get('rarita', ''), max=ev['player']['max_inventario'])}")
        for lv in ev["level_up"]:
            print(f"  {t('level_up_notice', level=lv['nuovo_livello'], hp_max=lv['hp_max'], att=lv['attacco'], dif=lv['difesa'], res_name=lv['risorsa_nome'], res_max=lv['risorsa_max'])}")
        mostra_stato_player(ev["player"])
    elif tipo == "fuga_riuscita":
        print(t("flee_success"))
        mostra_stato_player(ev["player"])
    elif tipo == "game_over":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ctx["mostro"]["nome"])
        print(t("game_over"))
    elif tipo == "errore_risorsa":
        print(f"\n! {ev['messaggio']}")
    elif tipo == "apertura_inventario":
        print(t("inv_title", used=ev["player"]["inventario_occupato"], max=ev["player"]["max_inventario"]))
        mostra_stato_player(ev["player"])
    elif tipo == "chiusura_inventario":
        print(t("inv_closed"))
    elif tipo == "oggetto_equipaggiato":
        msg = f"\n{t('equipped_msg', item=ev['item']['nome'])}"
        if ev.get("rimosso"):
            msg += t("swapped_msg", item=ev["rimosso"]["nome"])
        print(msg)
        mostra_stato_player(ev["player"])
    elif tipo == "oggetto_disequipaggiato":
        print(f"\n{ev.get('messaggio', '')}")
        mostra_stato_player(ev["player"])
    elif tipo == "oggetto_scartato":
        print(f"\n{t('discarded_msg', item=ev['item']['nome'])}")
        mostra_stato_player(ev["player"])
    elif tipo == "salvataggio_completato":
        print(f"\n[OK] {ev.get('messaggio', t('save_success'))}")
    elif tipo == "caricamento_completato":
        print(f"\n[OK] {ev.get('messaggio', t('load_success'))}")
        if ev.get("area"):
            ctx["uscite"] = ev["area"]["uscite_disponibili"]
            mostra_area(ev["area"])
        mostra_stato_player(ev["player"])
    elif tipo in ("errore", "mossa_bloccata"):
        print(f"\n! {ev['messaggio']}")


# =====================================================================
# INPUT UTENTE
# =====================================================================

def chiedi(prompt: str, valide: List[str]) -> str:
    while True:
        try:
            risposta = input(prompt).strip().lower()
        except EOFError:
            print("\nInput terminated: exiting game.")
            raise SystemExit(0)
        if risposta in valide:
            return risposta
        print(f"  {t('invalid_choice', options=', '.join(valide))}")


def scegli_classe() -> PlayerClass:
    classi = list(PlayerClass)
    print(t("select_class_title"))
    for i, c in enumerate(classi, start=1):
        pr = CLASS_PROFILES[c]
        c_nome = get_class_name(c)
        r_nome = get_resource_name(pr.risorsa_tipo)
        ab_nome = get_class_ability_name(c)
        ab_desc = get_class_ability_desc(c)
        print(f"  {i}) {c_nome:<12} HP {pr.hp_base}, {r_nome} {pr.risorsa_max_base} "
              f"- {ab_nome}: {ab_desc}")
    scelta = chiedi(t("class_prompt"), [str(i) for i in range(1, len(classi) + 1)])
    return classi[int(scelta) - 1]


# =====================================================================
# LOOP INTERATTIVO
# =====================================================================

def menu_esplorazione(engine: GameEngine, ctx: Dict[str, Any]) -> bool:
    uscite_display = [u for u in ctx.get("uscite", [])]
    opzioni = ["i", "q", "save", "salva"]

    # Accetta sia la lettera visualizzata che la corrispondente cardinale
    for u in uscite_display:
        u_low = u.lower()
        if u_low not in opzioni:
            opzioni.append(u_low)
        if u_low == "w" and "o" not in opzioni:
            opzioni.append("o")
        elif u_low == "o" and "w" not in opzioni:
            opzioni.append("w")

    if "s" not in uscite_display:
        opzioni.append("s")

    prompt = t("explore_prompt", exits="/".join(uscite_display))
    scelta = chiedi(prompt, opzioni)

    if scelta == "q":
        return False
    if scelta == "i":
        render_evento(engine.apri_inventario(), ctx)
    elif scelta in ("save", "salva") or (scelta == "s" and "s" not in [u.lower() for u in uscite_display]):
        render_evento(engine.salva_partita(), ctx)
    else:
        direzione = DIR_MAP[scelta]
        render_evento(engine.esplora(direzione), ctx)
    return True


def menu_combattimento(engine: GameEngine, ctx: Dict[str, Any]) -> None:
    assert engine.player is not None
    p = engine.player
    profilo = CLASS_PROFILES[p.classe]
    ab_nome = get_class_ability_name(p.classe)
    res_nome = get_resource_name(profilo.risorsa_tipo)

    prompt = t("combat_prompt", skill=ab_nome, cost=profilo.costo_risorsa, resource=res_nome)
    scelta = chiedi(prompt, ["a", "s", "o", "f", "i"])

    if scelta == "a":
        render_evento(engine.azione_combattimento(CombatAction.ATTACCA), ctx)
    elif scelta == "s":
        render_evento(engine.azione_combattimento(CombatAction.ABILITA_SPECIALE), ctx)
    elif scelta == "f":
        render_evento(engine.azione_combattimento(CombatAction.FUGGI), ctx)
    elif scelta == "i":
        render_evento(engine.apri_inventario(), ctx)
    elif scelta == "o":
        usabili = [i for i in engine.player.inventario if (i.cura_hp > 0 or i.cura_risorsa > 0)]
        if not usabili:
            print(t("no_usable_consumables"))
            return
        for n, oggetto in enumerate(usabili, start=1):
            effetti = []
            if oggetto.cura_hp > 0:
                effetti.append(f"+{oggetto.cura_hp} HP")
            if oggetto.cura_risorsa > 0:
                effetti.append(f"+{oggetto.cura_risorsa} {res_nome}")
            desc = ", ".join(effetti)
            print(f"  {n}) {oggetto.nome} ({desc})")
        idx = chiedi(t("use_item_prompt"), [str(n) for n in range(0, len(usabili) + 1)])
        if idx != "0":
            render_evento(engine.azione_combattimento(CombatAction.USA_OGGETTO, usabili[int(idx) - 1]), ctx)


def menu_inventario(engine: GameEngine, ctx: Dict[str, Any]) -> None:
    assert engine.player is not None
    player = engine.player
    inventario = player.inventario
    equip = player.equip
    occupati = len(inventario)
    capienza = player.max_inventario

    print(t("backpack_equip_title", used=occupati, max=capienza))
    print(f"  {t('active_weapon'):<18} {equip.arma.nome if equip.arma else t('none')}")
    print(f"  {t('active_armor'):<18} {equip.armatura.nome if equip.armatura else t('none')}")
    print(f"  {t('items_in_backpack')}")
    if not inventario:
        print(f"    {t('empty')}")
    else:
        for n, oggetto in enumerate(inventario, start=1):
            stats = []
            if oggetto.bonus_attacco:
                stats.append(f"+{oggetto.bonus_attacco} ATT")
            if oggetto.bonus_difesa:
                stats.append(f"+{oggetto.bonus_difesa} DIF")
            if oggetto.cura_hp:
                stats.append(f"+{oggetto.cura_hp} HP")
            if oggetto.cura_risorsa:
                stats.append(f"+{oggetto.cura_risorsa} {get_resource_name(player.risorsa_tipo)}")
            dettagli = f" ({', '.join(stats)})" if stats else ""
            r_str = get_rarity_name(oggetto.rarita)
            t_str = get_item_type_name(oggetto.tipo)
            print(f"    {n}) {oggetto.nome} [{r_str}] - {t_str}{dettagli}")
            mostra_sprite(oggetto.sprite_path)

    prompt = t("backpack_actions", used=occupati, max=capienza)
    scelta = chiedi(prompt, ["e", "d", "s", "0", "q"])

    if scelta in ("0", "q"):
        render_evento(engine.chiudi_inventario(), ctx)
        return

    if scelta == "e":
        if not inventario:
            print(t("backpack_empty_equip"))
            return
        idx = chiedi(t("equip_prompt"), [str(n) for n in range(0, len(inventario) + 1)])
        if idx == "0":
            return
        oggetto = inventario[int(idx) - 1]
        if oggetto.tipo not in (ItemType.ARMA, ItemType.ARMATURA):
            print(t("not_equippable", item=oggetto.nome, type=get_item_type_name(oggetto.tipo)))
            return
        render_evento(engine.equipaggia_oggetto(oggetto), ctx)

    elif scelta == "d":
        slot_attivi = []
        if equip.arma:
            slot_attivi.append("arma")
        if equip.armatura:
            slot_attivi.append("armatura")

        if not slot_attivi:
            print(t("no_active_equip"))
            return

        if len(inventario) >= player.max_inventario:
            print(t("inventory_full_unequip", used=len(inventario), max=player.max_inventario))
            return

        print(t("active_slots_title"))
        opzioni = ["0", "q"]
        if equip.arma:
            print(f"  {t('slot_weapon_label', item=equip.arma.nome)}")
            opzioni.extend(["1", "arma", "a", "weapon", "w"])
        if equip.armatura:
            print(f"  {t('slot_armor_label', item=equip.armatura.nome)}")
            opzioni.extend(["2", "armatura", "armor"])

        scelta_slot = chiedi(t("unequip_prompt"), opzioni)
        if scelta_slot in ("0", "q"):
            return
        slot_target = "arma" if scelta_slot in ("1", "arma", "a", "weapon", "w") else "armatura"
        render_evento(engine.disequipaggia_slot(slot_target), ctx)

    elif scelta == "s":
        if not inventario:
            print(t("backpack_empty_discard"))
            return
        idx = chiedi(t("discard_prompt"), [str(n) for n in range(0, len(inventario) + 1)])
        if idx == "0":
            return
        oggetto = inventario[int(idx) - 1]
        conferma = chiedi(t("discard_confirm", item=oggetto.nome), ["s", "n", "y"])
        if conferma in ("s", "y"):
            render_evento(engine.scarta_oggetto(oggetto), ctx)


def loop_interattivo(engine: GameEngine) -> None:
    ctx: Dict[str, Any] = {}

    if engine.esiste_salvataggio():
        print(f"\n{t('game_title')}")
        print(f"  {t('menu_new_game')}")
        print(f"  {t('menu_load_game')}")
        print(f"  {t('menu_quit')}")
        scelta_avvio = chiedi(t("choice_prompt"), ["1", "2", "q"])
        if scelta_avvio == "q":
            print(t("farewell"))
            return
        elif scelta_avvio == "2":
            ev = engine.carica_partita()
            render_evento(ev, ctx)
            if ev.get("tipo") == "errore":
                print(t("starting_new_game"))
                scelta_avvio = "1"

        if scelta_avvio == "1":
            try:
                nome = input(t("hero_name_prompt")).strip() or t("default_hero_name")
            except EOFError:
                raise SystemExit(0)
            classe = scegli_classe()
            render_evento(engine.nuova_partita(nome, classe), ctx)
    else:
        try:
            nome = input(t("hero_name_prompt")).strip() or t("default_hero_name")
        except EOFError:
            raise SystemExit(0)
        classe = scegli_classe()
        render_evento(engine.nuova_partita(nome, classe), ctx)

    while True:
        stato = engine.state
        if stato == GameState.SELEZIONE_ZONA:
            zone = list(engine.aree.values())
            print(t("select_zone_title"))
            for n, zona in enumerate(zone, start=1):
                print(f"  {n}) {zona.nome} - {zona.descrizione}")
            scelta = chiedi(t("zone_prompt"), [str(n) for n in range(1, len(zone) + 1)])
            render_evento(engine.seleziona_zona(zone[int(scelta) - 1].id), ctx)
        elif stato == GameState.ESPLORAZIONE:
            if not menu_esplorazione(engine, ctx):
                print(t("farewell"))
                return
        elif stato == GameState.COMBATTIMENTO:
            menu_combattimento(engine, ctx)
        elif stato == GameState.INVENTARIO:
            menu_inventario(engine, ctx)
        elif stato == GameState.VITTORIA:
            scelta_fine = chiedi(t("play_again_prompt"), ["1", "q"])
            if scelta_fine == "1":
                try:
                    nome = input(t("hero_name_prompt")).strip() or t("default_hero_name")
                except EOFError:
                    raise SystemExit(0)
                classe = scegli_classe()
                render_evento(engine.nuova_partita(nome, classe), ctx)
            else:
                print(t("thanks_playing"))
                return
        else:
            return


def loop_demo(engine: GameEngine, classe: PlayerClass) -> None:
    ctx: Dict[str, Any] = {}
    render_evento(engine.nuova_partita("Aria", classe), ctx)
    render_evento(engine.seleziona_zona("ingresso"), ctx)
    assert engine.player is not None
    profilo = CLASS_PROFILES[classe]

    for _ in range(PASSI_DEMO):
        if engine.state == GameState.ESPLORAZIONE:
            scelta_raw = random.choice(ctx["uscite"])
            direzione = DIR_MAP[scelta_raw.lower()]
            render_evento(engine.esplora(direzione), ctx)
        elif engine.state == GameState.COMBATTIMENTO:
            p = engine.player
            pozioni = [i for i in p.inventario if (i.cura_hp > 0 or i.cura_risorsa > 0)]
            if p.hp_corrente < 0.4 * p.hp_max and pozioni:
                ev = engine.azione_combattimento(CombatAction.USA_OGGETTO, pozioni[0])
            elif p.risorsa_corrente >= profilo.costo_risorsa and not p.effetti_attivi:
                ev = engine.azione_combattimento(CombatAction.ABILITA_SPECIALE)
            else:
                ev = engine.azione_combattimento(CombatAction.ATTACCA)
            render_evento(ev, ctx)
        elif engine.state == GameState.VITTORIA:
            print(t("demo_triumph"))
            break
        else:
            break

    print(t("demo_end"))
    for riga in engine.log[-8:]:
        print(f" - {riga}")


def main(argv: Optional[List[str]] = None) -> int:
    class_cli_map = {
        "guerriero": PlayerClass.GUERRIERO,
        "warrior": PlayerClass.GUERRIERO,
        "mago": PlayerClass.MAGO,
        "mage": PlayerClass.MAGO,
        "cavaliere": PlayerClass.CAVALIERE,
        "knight": PlayerClass.CAVALIERE,
        "medico": PlayerClass.MEDICO,
        "cleric": PlayerClass.MEDICO,
        "medic": PlayerClass.MEDICO,
    }
    parser = argparse.ArgumentParser(description="Dungiasi RPG - Dungeon Crawler GDR testuale a turni")
    parser.add_argument("--demo", action="store_true", help="esegue una partita automatica / run automated bot demo")
    parser.add_argument("--classe", choices=list(class_cli_map.keys()),
                        default="guerriero", help="classe usata in modalita' --demo (es. warrior, mage, knight, cleric)")
    parser.add_argument("--seed", type=int, default=None, help="seed del generatore casuale")
    parser.add_argument("--window", "--gui", action="store_true", dest="window",
                        help="avvia il visualizzatore grafico companion (richiede Tkinter)")
    parser.add_argument("--lang", choices=["it", "en"], default=None,
                        help="seleziona la lingua: it (italiano) o en (english)")
    args = parser.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    # Scelta della lingua: da flag CLI oppure schermata iniziale
    if args.lang:
        set_language(args.lang)
    elif not args.demo:
        seleziona_lingua_interattiva()
    else:
        set_language("it")

    if args.window:
        avvia_gui_companion(titolo=t("asset_viewer_title"))

    engine = GameEngine()
    popola_mondo(engine)

    try:
        if args.demo:
            loop_demo(engine, class_cli_map[args.classe.lower()])
        else:
            loop_interattivo(engine)
    except KeyboardInterrupt:
        print("\n" + t("farewell"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
