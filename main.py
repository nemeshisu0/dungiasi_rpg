"""
main.py
=======
Frontend CLI del dungeon crawler: unico modulo con print()/input().
Include hook per visualizzazione sprite tramite tool CLI (chafa) o fallback.
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
from world import popola_mondo

LARGHEZZA_BARRA = 20
PASSI_DEMO = 60


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
        print(f"\n[GUI Companion] Impossibile inizializzare Tkinter ({exc}). Fallback su terminale.")
        return

    try:
        root = tk.Tk()
        root.title(titolo)
        root.geometry(dimensioni)
        root.resizable(True, True)

        header = tk.Label(root, text="Dungiasi RPG - Asset Viewer", font=("Helvetica", 11, "bold"))
        header.pack(pady=6)

        img_label = tk.Label(root, text="(In attesa del primo evento di gioco...)")
        img_label.pack(expand=True, fill="both", padx=10, pady=10)

        status_label = tk.Label(root, text="Pronto", font=("Helvetica", 9, "italic"))
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
                            status_label.config(text=f"Asset: {os.path.basename(sprite_path)}")
                        except Exception as e:
                            status_label.config(text=f"Errore caricamento: {os.path.basename(sprite_path)}")
                    elif sprite_path:
                        status_label.config(text=f"Asset non trovato: {os.path.basename(sprite_path)}")
            except Exception:
                pass
            root.after(100, process_queue)

        root.after(100, process_queue)
        root.mainloop()
    except Exception as exc:
        print(f"\n[GUI Companion] Finestra non avviabile ({exc}). Fallback su terminale.")


def avvia_gui_companion(titolo: str = GUI_WINDOW_TITLE, dimensioni: str = GUI_WINDOW_SIZE) -> bool:
    """Avvia la finestra companion in un thread daemon separato."""
    global _gui_queue, _gui_thread
    try:
        import tkinter  # verifica preventiva rapida
    except Exception as exc:
        print(f"\n[GUI Companion] Tkinter non disponibile ({exc}). Continuo solo su terminale.")
        return False

    _gui_queue = queue.Queue()
    _gui_thread = threading.Thread(
        target=_gui_worker,
        args=(_gui_queue, titolo, dimensioni),
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
            # Se siamo su terminale Kitty, prova prima il protocollo grafico diretto
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

            # Rendering terminale nitido per pixel art (vhalf, dither=none)
            try:
                res = subprocess.run(
                    ["chafa"] + CHAFA_ARGS_PIXEL_ART + [sprite_path],
                    check=False,
                )
                if res.returncode == 0:
                    return
            except Exception:
                pass

        # In alternativa su Kitty con kitty icat se installato
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

    # Fallback elegante se chafa non e' presente o il PNG non e' stato trovato
    print(f"   [sprite: {sprite_path}]")


def barra(corrente: int, massimo: int) -> str:
    massimo = max(1, massimo)
    pieni = round(LARGHEZZA_BARRA * max(0, corrente) / massimo)
    return "[" + "#" * pieni + "-" * (LARGHEZZA_BARRA - pieni) + "]"


def mostra_stato_player(p: Dict[str, Any]) -> None:
    zaino_info = f"  Zaino {p['inventario_occupato']}/{p['max_inventario']}" if "max_inventario" in p else ""
    print(f"\n{p['nome']} ({p['classe']}) Lv.{p['livello']}  "
          f"EXP {p['exp']}/{p['exp_richiesta']}  Oro {p['oro']}{zaino_info}  "
          f"ATT {p['attacco']}  DIF {p['difesa']}")
    print(f"  HP      {barra(p['hp_corrente'], p['hp_max'])} {p['hp_corrente']}/{p['hp_max']}")
    print(f"  {p['risorsa_nome']:<7} {barra(p['risorsa_corrente'], p['risorsa_max'])} "
          f"{p['risorsa_corrente']}/{p['risorsa_max']}")
    if p["effetti_attivi"]:
        effetti = ", ".join(f"{n} ({t} turni)" for n, t in p["effetti_attivi"].items())
        print(f"  Effetti: {effetti}")


def mostra_mostro(m: Dict[str, Any]) -> None:
    print(f"\n  {m['nome']} (Lv.{m['livello']})  "
          f"HP {barra(m['hp_corrente'], m['hp_max'])} {m['hp_corrente']}/{m['hp_max']}")


def mostra_area(a: Dict[str, Any]) -> None:
    print(f"\n=== {a['nome']} ===")
    print(a["descrizione"])
    mostra_sprite(a["sprite_path"])
    print("Uscite:", ", ".join(a["uscite_disponibili"]))


def racconta_evento_turno(e: Dict[str, Any], nome_mostro: str) -> None:
    tipo = e["tipo"]
    if tipo == "attacco_player":
        extra = ""
        if e.get("risorsa_guadagnata"):
            extra = f" (+{e['risorsa_guadagnata']} risorsa)"
        elif e.get("risorsa_consumata"):
            extra = f" (-{e['risorsa_consumata']} risorsa)"
        prefisso = "Sferri un Colpo Affaticato a" if e.get("affaticato") else "Colpisci"
        print(f"  {prefisso} {nome_mostro}: {e['danno']} danni.{extra}")
    elif tipo == "abilita_speciale":
        if "danno" in e:
            dettaglio = f"{e['danno']} danni"
        elif "hp_curati" in e:
            dettaglio = f"{e['hp_curati']} HP recuperati"
        else:
            dettaglio = f"{e['buff_attivato']} attivo per {e['turni_buff']} turni"
        print(f"  {e['nome_abilita']}! {dettaglio} (-{e['risorsa_consumata']} {e['risorsa_nome']})")
    elif tipo == "uso_oggetto":
        parti = []
        if e.get("hp_curati", 0) > 0:
            parti.append(f"+{e['hp_curati']} HP")
        if e.get("risorsa_curata", 0) > 0:
            parti.append(f"+{e['risorsa_curata']} {e['player']['risorsa_nome']}")
        recupero = ", ".join(parti) if parti else "nessun effetto"
        print(f"  Usi {e['item']['nome']}: {recupero}.")
    elif tipo == "fuga_fallita":
        print("  Non riesci a fuggire!")
    elif tipo == "attacco_mostro":
        extra = f" (+{e['risorsa_guadagnata']} risorsa)" if e.get("risorsa_guadagnata") else ""
        print(f"  {nome_mostro} ti colpisce: {e['danno']} danni.{extra}")
        if e.get("contrattacco_baluardo"):
            print(f"  Il Baluardo riflette {e['contrattacco_baluardo']} danni!")
    elif tipo == "fase_boss":
        print(f"\n  >>> {e['messaggio']} <<<")
    elif tipo == "attacco_boss":
        print(f"  {nome_mostro} scatena {e['nome_abilita']}! {e['danno']} DANNI DEVASTANTI!")


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
            print("!!!           ATTENZIONE: SCONTRO BOSS FINALE            !!!")
            print(f"!!!                 {ev['mostro']['nome'].upper()}                   !!!")
            print("=" * 60)
        else:
            print(f"\n!!! Un {ev['mostro']['nome']} ti sbarra la strada !!!")
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
        print("***       TRIONFO EPICO: IL BOSS FINALE E' STATO ABBATTUTO!     ***")
        print("*" * 64)
        print(f"\n  Il temibile {ev['mostro_sconfitto']['nome']} e' caduto al suolo!")
        print(f"  Hai ottenuto +{ev['exp_ottenuta']} EXP e +{ev['oro_ottenuto']} oro.")
        for oggetto in ev["drop"]:
            print(f"  Bottino leggendario: {oggetto['nome']} ({oggetto['rarita']})")
            mostra_sprite(oggetto["sprite_path"])
        for oggetto_perso in ev.get("drop_persi", []):
            print(f"  [!] Inventario pieno: {oggetto_perso['nome']} lasciato a terra.")

        st = ev.get("statistiche", {})
        print("\n" + "=" * 50)
        print("            STATISTICHE DI FINE PARTITA")
        print("=" * 50)
        print(f"  Eroe:                {ev['player']['nome']} ({st.get('classe', ev['player']['classe'])})")
        print(f"  Livello raggiunto:   Lv.{st.get('livello_raggiunto', ev['player']['livello'])}")
        print(f"  Oro accumulato:      {st.get('oro_totale', ev['player']['oro'])}")
        print(f"  Mostri sconfitti:    {st.get('mostri_sconfitti', 0)}")
        print(f"  Turni combattuti:    {st.get('turni_combattimento', 0)}")
        print(f"  Salute residua:      {st.get('hp_finali', '')}")
        print("=" * 50)
        print("\nComplimenti! Hai liberato il dungeon e scritto il tuo nome nella leggenda!\n")
        mostra_stato_player(ev["player"])
    elif tipo == "vittoria_combattimento":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ev["mostro_sconfitto"]["nome"])
        print(f"\n*** {ev['mostro_sconfitto']['nome']} sconfitto! ***  "
              f"+{ev['exp_ottenuta']} EXP, +{ev['oro_ottenuto']} oro")
        for oggetto in ev["drop"]:
            print(f"  Bottino: {oggetto['nome']} ({oggetto['rarita']})")
            mostra_sprite(oggetto["sprite_path"])
        for oggetto_perso in ev.get("drop_persi", []):
            print(f"  [!] Inventario pieno ({ev['player']['max_inventario']}/{ev['player']['max_inventario']}): "
                  f"{oggetto_perso['nome']} ({oggetto_perso['rarita']}) lasciato a terra!")
        for lv in ev["level_up"]:
            print(f"  LEVEL UP! Livello {lv['nuovo_livello']}: HP max {lv['hp_max']}, "
                  f"ATT {lv['attacco']}, DIF {lv['difesa']}, {lv['risorsa_nome']} max {lv['risorsa_max']}")
        mostra_stato_player(ev["player"])
    elif tipo == "fuga_riuscita":
        print("\nSei riuscito a fuggire!")
        mostra_stato_player(ev["player"])
    elif tipo == "game_over":
        for e in ev["eventi"]:
            racconta_evento_turno(e, ctx["mostro"]["nome"])
        print("\n### SEI STATO SCONFITTO - GAME OVER ###")
    elif tipo == "errore_risorsa":
        print(f"\n! {ev['messaggio']}")
    elif tipo == "apertura_inventario":
        print(f"\n--- INVENTARIO (Zaino: {ev['player']['inventario_occupato']}/{ev['player']['max_inventario']} slot) ---")
        mostra_stato_player(ev["player"])
    elif tipo == "chiusura_inventario":
        print("\nInventario chiuso.")
    elif tipo == "oggetto_equipaggiato":
        msg = f"\nEquipaggiato: {ev['item']['nome']}"
        if ev.get("rimosso"):
            msg += f" (Riposto nell'inventario: {ev['rimosso']['nome']})"
        print(msg)
        mostra_stato_player(ev["player"])
    elif tipo == "oggetto_disequipaggiato":
        msg = f"\n{ev.get('messaggio', 'Oggetto disequipaggiato.')}"
        print(msg)
        mostra_stato_player(ev["player"])
    elif tipo == "oggetto_scartato":
        print(f"\nHai scartato: {ev['item']['nome']}.")
        mostra_stato_player(ev["player"])
    elif tipo == "salvataggio_completato":
        print(f"\n[OK] {ev.get('messaggio', 'Partita salvata con successo!')}")
    elif tipo == "caricamento_completato":
        print(f"\n[OK] {ev.get('messaggio', 'Partita caricata con successo!')}")
        if ev.get("area"):
            ctx["uscite"] = ev["area"]["uscite_disponibili"]
            mostra_area(ev["area"])
        mostra_stato_player(ev["player"])
    elif tipo in ("errore", "mossa_bloccata"):
        print(f"\n! {ev['messaggio']}")


# =====================================================================
# INPUT
# =====================================================================

def chiedi(prompt: str, valide: List[str]) -> str:
    while True:
        try:
            risposta = input(prompt).strip().lower()
        except EOFError:
            print("\nInput terminato: uscita dal gioco.")
            raise SystemExit(0)
        if risposta in valide:
            return risposta
        print(f"  Scelta non valida. Opzioni: {', '.join(valide)}")


def scegli_classe() -> PlayerClass:
    classi = list(PlayerClass)
    print("\nScegli la tua classe:")
    for i, c in enumerate(classi, start=1):
        pr = CLASS_PROFILES[c]
        print(f"  {i}) {c.value:<10} HP {pr.hp_base}, {pr.risorsa_tipo.value} {pr.risorsa_max_base} "
              f"- {pr.nome_abilita}: {pr.descrizione_abilita}")
    scelta = chiedi("Classe (numero): ", [str(i) for i in range(1, len(classi) + 1)])
    return classi[int(scelta) - 1]


# =====================================================================
# LOOP INTERATTIVO
# =====================================================================

def menu_esplorazione(engine: GameEngine, ctx: Dict[str, Any]) -> bool:
    uscite = [u.lower() for u in ctx.get("uscite", [])]
    opzioni = list(uscite) + ["i", "q", "save", "salva"]
    if "s" not in uscite:
        opzioni.append("s")

    scelta = chiedi(
        f"\nDove vai? [{'/'.join(u.upper() for u in uscite)}] "
        f"(i = inventario, save = salva, q = esci): ",
        opzioni,
    )
    if scelta == "q":
        return False
    if scelta == "i":
        render_evento(engine.apri_inventario(), ctx)
    elif scelta in ("save", "salva") or (scelta == "s" and "s" not in uscite):
        render_evento(engine.salva_partita(), ctx)
    else:
        render_evento(engine.esplora(Direction(scelta.upper())), ctx)
    return True



def menu_combattimento(engine: GameEngine, ctx: Dict[str, Any]) -> None:
    assert engine.player is not None
    profilo = CLASS_PROFILES[engine.player.classe]
    scelta = chiedi(
        f"\n[a] Attacca  [s] {profilo.nome_abilita} ({profilo.costo_risorsa} {profilo.risorsa_tipo.value})  "
        f"[o] Oggetto  [f] Fuggi  [i] Inventario: ",
        ["a", "s", "o", "f", "i"],
    )
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
            print("\n! Nessun consumabile utilizzabile.")
            return
        for n, oggetto in enumerate(usabili, start=1):
            effetti = []
            if oggetto.cura_hp > 0:
                effetti.append(f"+{oggetto.cura_hp} HP")
            if oggetto.cura_risorsa > 0:
                effetti.append(f"+{oggetto.cura_risorsa} Risorsa")
            desc = ", ".join(effetti)
            print(f"  {n}) {oggetto.nome} ({desc})")
        idx = chiedi("Oggetto (0 = annulla): ", [str(n) for n in range(0, len(usabili) + 1)])
        if idx != "0":
            render_evento(engine.azione_combattimento(CombatAction.USA_OGGETTO, usabili[int(idx) - 1]), ctx)


def menu_inventario(engine: GameEngine, ctx: Dict[str, Any]) -> None:
    assert engine.player is not None
    player = engine.player
    inventario = player.inventario
    equip = player.equip
    occupati = len(inventario)
    capienza = player.max_inventario

    print(f"\n=== ZAINO E EQUIPAGGIAMENTO (Zaino: {occupati}/{capienza} slot) ===")
    print(f"  Arma attiva:     {equip.arma.nome if equip.arma else '(nessuna)'}")
    print(f"  Armatura attiva: {equip.armatura.nome if equip.armatura else '(nessuna)'}")
    print("  Oggetti nello zaino:")
    if not inventario:
        print("    (vuoto)")
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
                stats.append(f"+{oggetto.cura_risorsa} Risorsa")
            dettagli = f" ({', '.join(stats)})" if stats else ""
            print(f"    {n}) {oggetto.nome} [{oggetto.rarita.value}] - {oggetto.tipo.value}{dettagli}")
            mostra_sprite(oggetto.sprite_path)

    scelta = chiedi(
        f"\nAzioni zaino (Zaino: {occupati}/{capienza} slot):\n"
        "  [e] Equipaggia  [d] Disequipaggia  [s] Scarta  [0/q] Torna indietro: ",
        ["e", "d", "s", "0", "q"],
    )

    if scelta in ("0", "q"):
        render_evento(engine.chiudi_inventario(), ctx)
        return

    if scelta == "e":
        if not inventario:
            print("\n! Lo zaino e' vuoto, nessun oggetto da equipaggiare.")
            return
        idx = chiedi(
            "Numero oggetto da equipaggiare (0 = annulla): ",
            [str(n) for n in range(0, len(inventario) + 1)],
        )
        if idx == "0":
            return
        oggetto = inventario[int(idx) - 1]
        if oggetto.tipo not in (ItemType.ARMA, ItemType.ARMATURA):
            print(f"\n! {oggetto.nome} non e' equipaggiabile (tipo: {oggetto.tipo.value}).")
            return
        render_evento(engine.equipaggia_oggetto(oggetto), ctx)

    elif scelta == "d":
        slot_attivi = []
        if equip.arma:
            slot_attivi.append("arma")
        if equip.armatura:
            slot_attivi.append("armatura")

        if not slot_attivi:
            print("\n! Nessun equipaggiamento attivo da disequipaggiare.")
            return

        if len(inventario) >= player.max_inventario:
            print(f"\n! Inventario pieno ({len(inventario)}/{player.max_inventario}): "
                  f"libera spazio nello zaino prima di disequipaggiare.")
            return

        print("\nSlot attivi:")
        opzioni = ["0", "q"]
        if equip.arma:
            print(f"  [1/arma]     Arma ({equip.arma.nome})")
            opzioni.extend(["1", "arma", "a"])
        if equip.armatura:
            print(f"  [2/armatura] Armatura ({equip.armatura.nome})")
            opzioni.extend(["2", "armatura"])

        scelta_slot = chiedi("Quale slot disequipaggiare? (0 = annulla): ", opzioni)
        if scelta_slot in ("0", "q"):
            return
        slot_target = "arma" if scelta_slot in ("1", "arma", "a") else "armatura"
        render_evento(engine.disequipaggia_slot(slot_target), ctx)

    elif scelta == "s":
        if not inventario:
            print("\n! Lo zaino e' vuoto, nessun oggetto da scartare.")
            return
        idx = chiedi(
            "Numero oggetto da scartare (0 = annulla): ",
            [str(n) for n in range(0, len(inventario) + 1)],
        )
        if idx == "0":
            return
        oggetto = inventario[int(idx) - 1]
        conferma = chiedi(f"Confermi di voler buttare via '{oggetto.nome}'? [s/n]: ", ["s", "n"])
        if conferma == "s":
            render_evento(engine.scarta_oggetto(oggetto), ctx)


def loop_interattivo(engine: GameEngine) -> None:
    ctx: Dict[str, Any] = {}

    if engine.esiste_salvataggio():
        print("\n=== DUNGIASI RPG ===")
        print("  [1] Nuova Partita")
        print("  [2] Carica Partita")
        print("  [q] Esci")
        scelta_avvio = chiedi("Scelta: ", ["1", "2", "q"])
        if scelta_avvio == "q":
            print("\nA presto, avventuriero!")
            return
        elif scelta_avvio == "2":
            ev = engine.carica_partita()
            render_evento(ev, ctx)
            if ev.get("tipo") == "errore":
                print("Avvio di una nuova partita...")
                scelta_avvio = "1"

        if scelta_avvio == "1":
            try:
                nome = input("\nNome dell'eroe: ").strip() or "Eroe"
            except EOFError:
                raise SystemExit(0)
            classe = scegli_classe()
            render_evento(engine.nuova_partita(nome, classe), ctx)
    else:
        try:
            nome = input("Nome dell'eroe: ").strip() or "Eroe"
        except EOFError:
            raise SystemExit(0)
        classe = scegli_classe()
        render_evento(engine.nuova_partita(nome, classe), ctx)

    while True:
        stato = engine.state
        if stato == GameState.SELEZIONE_ZONA:
            zone = list(engine.aree.values())
            print("\nZone disponibili:")
            for n, zona in enumerate(zone, start=1):
                print(f"  {n}) {zona.nome} - {zona.descrizione}")
            scelta = chiedi("Zona (numero): ", [str(n) for n in range(1, len(zone) + 1)])
            render_evento(engine.seleziona_zona(zone[int(scelta) - 1].id), ctx)
        elif stato == GameState.ESPLORAZIONE:
            if not menu_esplorazione(engine, ctx):
                print("\nA presto, avventuriero!")
                return
        elif stato == GameState.COMBATTIMENTO:
            menu_combattimento(engine, ctx)
        elif stato == GameState.INVENTARIO:
            menu_inventario(engine, ctx)
        elif stato == GameState.VITTORIA:
            scelta_fine = chiedi("\nDesideri iniziare una nuova partita o uscire? [1 = nuova partita, q = esci]: ", ["1", "q"])
            if scelta_fine == "1":
                try:
                    nome = input("\nNome dell'eroe: ").strip() or "Eroe"
                except EOFError:
                    raise SystemExit(0)
                classe = scegli_classe()
                render_evento(engine.nuova_partita(nome, classe), ctx)
            else:
                print("\nGrazie per aver giocato! Gloria al vincitore!")
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
            direzione = Direction(random.choice(ctx["uscite"]))
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
            print("\n*** Conclusione trionfale della modalita' Demo: Boss sconfitto! ***")
            break
        else:
            break

    print("\n--- Fine demo. Ultimi messaggi di log ---")
    for riga in engine.log[-8:]:
        print(f" - {riga}")


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Dungiasi RPG - Dungeon Crawler GDR testuale a turni")
    parser.add_argument("--demo", action="store_true", help="esegue una partita automatica")
    parser.add_argument("--classe", choices=[c.name.lower() for c in PlayerClass],
                        default="guerriero", help="classe usata in modalita' --demo")
    parser.add_argument("--seed", type=int, default=None, help="seed del generatore casuale")
    parser.add_argument("--window", "--gui", action="store_true", dest="window",
                        help="avvia il visualizzatore grafico companion (richiede Tkinter)")
    args = parser.parse_args(argv)

    if args.seed is not None:
        random.seed(args.seed)

    if args.window:
        avvia_gui_companion()

    engine = GameEngine()
    popola_mondo(engine)

    try:
        if args.demo:
            loop_demo(engine, PlayerClass[args.classe.upper()])
        else:
            loop_interattivo(engine)
    except KeyboardInterrupt:
        print("\nInterrotto dall'utente.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
