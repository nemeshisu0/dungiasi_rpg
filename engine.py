"""
engine.py
=========
Game Engine (logica pura): macchina a stati, esplorazione, combattimento,
progressione e inventario.
"""

from __future__ import annotations

import json
import os
import random
from typing import Any, Dict, List, Optional

from config import (
    BALUARDO_DURATA_TURNI,
    BALUARDO_PERC_RIFLESSO,
    CHANCE_FUGA,
    CLASS_PROFILES,
    COLPO_DEVASTANTE_DIFESA,
    COLPO_DEVASTANTE_MOLT,
    DARDO_ARCANO_MOLT,
    EFFETTO_BALUARDO,
    FURIA_PER_ATTACCO,
    FURIA_PER_DANNO_SUBITO,
    PRONTO_SOCCORSO_PERC,
    REGEN_TURNO_CAVALIERE,
    REGEN_TURNO_MAGO,
    REGEN_TURNO_MEDICO,
    STAMINA_COSTO_ATTACCO,
    ClassProfile,
    CombatAction,
    Direction,
    GameState,
    PlayerClass,
)
from formulas import calcola_danno, exp_richiesta_per_livello, tira_drop
from models import Area, Item, Monster, Player


class GameEngine:
    """Cuore del gioco: gestisce stato, dati e regole. Nessun I/O diretto."""

    def __init__(self) -> None:
        self.state: GameState = GameState.MENU
        self.player: Optional[Player] = None
        self.aree: Dict[str, Area] = {}
        self.area_corrente: Optional[Area] = None
        self.mostro_corrente: Optional[Monster] = None
        self._stato_prima_combattimento: GameState = GameState.ESPLORAZIONE
        self._stato_prima_inventario: GameState = GameState.ESPLORAZIONE
        self.log: List[str] = []
        self.mostri_sconfitti: int = 0
        self.turni_combattimento: int = 0

    def _log(self, messaggio: str) -> None:
        self.log.append(messaggio)

    def _evento(self, tipo: str, **payload: Any) -> Dict[str, Any]:
        return {"tipo": tipo, "state": self.state.name, **payload}

    def registra_area(self, area: Area) -> None:
        self.aree[area.id] = area

    def nuova_partita(self, nome_player: str, classe: PlayerClass) -> Dict[str, Any]:
        self.player = Player(nome=nome_player, classe=classe)
        self.area_corrente = None
        self.mostro_corrente = None
        self.log.clear()
        self.mostri_sconfitti = 0
        self.turni_combattimento = 0
        self.state = GameState.SELEZIONE_ZONA
        self._log(f"Nuova partita iniziata per {nome_player} ({classe.value}).")
        return self._evento(
            "nuova_partita",
            player=self.player.to_render_dict(),
            zone_disponibili=[a.to_render_dict() for a in self.aree.values()],
        )

    def seleziona_zona(self, area_id: str) -> Dict[str, Any]:
        if self.state != GameState.SELEZIONE_ZONA:
            return self._evento("errore", messaggio="Non e' possibile selezionare una zona ora.")
        area = self.aree.get(area_id)
        if area is None:
            return self._evento("errore", messaggio=f"Zona '{area_id}' inesistente.")
        self.area_corrente = area
        self.state = GameState.ESPLORAZIONE
        self._log(f"Sei entrato in: {area.nome}")
        return self._evento("ingresso_area", area=area.to_render_dict())

    def esplora(self, direzione: Direction) -> Dict[str, Any]:
        if self.state != GameState.ESPLORAZIONE or self.area_corrente is None:
            return self._evento("errore", messaggio="Non sei in fase di esplorazione.")

        if direzione not in self.area_corrente.uscite:
            return self._evento("mossa_bloccata", messaggio="Non puoi proseguire in quella direzione.")

        if random.random() < self.area_corrente.chance_incontro:
            evento = self._avvia_combattimento()
            if evento is not None:
                return evento

        prossima_id = self.area_corrente.uscite[direzione]
        prossima_area = self.aree.get(prossima_id)
        if prossima_area is None:
            return self._evento("errore", messaggio=f"Area di destinazione '{prossima_id}' non trovata.")

        self.area_corrente = prossima_area
        self._log(f"Ti sei spostato verso: {prossima_area.nome}")
        return self._evento("spostamento", area=prossima_area.to_render_dict())

    def _avvia_combattimento(self) -> Optional[Dict[str, Any]]:
        assert self.area_corrente is not None and self.player is not None
        mostro = self.area_corrente.mostro_casuale()
        if mostro is None:
            return None

        self.mostro_corrente = mostro
        self._stato_prima_combattimento = GameState.ESPLORAZIONE
        self.state = GameState.COMBATTIMENTO
        self.player.inizializza_risorsa_per_incontro()
        self.player.effetti_attivi.clear()
        self._log(f"Un {mostro.nome} selvatico appare!")
        return self._evento(
            "incontro",
            mostro=mostro.to_render_dict(),
            player=self.player.to_render_dict(),
        )

    def azione_combattimento(
        self, azione: CombatAction, item: Optional[Item] = None
    ) -> Dict[str, Any]:
        if (
            self.state != GameState.COMBATTIMENTO
            or self.mostro_corrente is None
            or self.player is None
        ):
            return self._evento("errore", messaggio="Non sei in combattimento.")

        player = self.player
        mostro = self.mostro_corrente
        profilo = CLASS_PROFILES[player.classe]
        eventi_turno: List[Dict[str, Any]] = []
        self.turni_combattimento += 1

        if azione == CombatAction.ATTACCA:
            danno_grezzo = calcola_danno(player.attacco_totale, mostro.difesa)
            affaticato = False

            if player.classe == PlayerClass.GUERRIERO:
                inflitto = mostro.subisci_danno(danno_grezzo)
                guadagno = player.guadagna_risorsa(FURIA_PER_ATTACCO)
                self._log(f"{player.nome} infligge {inflitto} danni a {mostro.nome}.")
                eventi_turno.append({
                    "tipo": "attacco_player", "danno": inflitto,
                    "risorsa_guadagnata": guadagno, "affaticato": False,
                    "mostro": mostro.to_render_dict(),
                })

            elif player.classe == PlayerClass.CAVALIERE:
                if player.risorsa_corrente < STAMINA_COSTO_ATTACCO:
                    affaticato = True
                    danno_grezzo *= 0.5
                    consumo = player.consuma_risorsa(player.risorsa_corrente)
                    inflitto = mostro.subisci_danno(danno_grezzo)
                    self._log(f"{player.nome} e' esausto e sferra un Colpo Affaticato per {inflitto} danni a {mostro.nome}!")
                else:
                    consumo = player.consuma_risorsa(STAMINA_COSTO_ATTACCO)
                    inflitto = mostro.subisci_danno(danno_grezzo)
                    self._log(f"{player.nome} infligge {inflitto} danni a {mostro.nome}.")

                eventi_turno.append({
                    "tipo": "attacco_player", "danno": inflitto,
                    "risorsa_consumata": consumo, "affaticato": affaticato,
                    "mostro": mostro.to_render_dict(),
                })

            else:
                inflitto = mostro.subisci_danno(danno_grezzo)
                self._log(f"{player.nome} infligge {inflitto} danni a {mostro.nome}.")
                eventi_turno.append({
                    "tipo": "attacco_player", "danno": inflitto, "affaticato": False,
                    "mostro": mostro.to_render_dict(),
                })

        elif azione == CombatAction.USA_OGGETTO:
            if item is None or item not in player.inventario:
                return self._evento("errore", messaggio="Oggetto non valido o non posseduto.")
            if item.cura_hp <= 0 and item.cura_risorsa <= 0:
                return self._evento("errore", messaggio=f"{item.nome} non e' utilizzabile.")
            eventi_turno.append(self._usa_oggetto_in_combattimento(item))

        elif azione == CombatAction.ABILITA_SPECIALE:
            if player.risorsa_corrente < profilo.costo_risorsa:
                return self._evento(
                    "errore_risorsa",
                    messaggio=(
                        f"{profilo.risorsa_tipo.value} insufficiente per usare "
                        f"{profilo.nome_abilita} (richiesti {profilo.costo_risorsa})."
                    ),
                    risorsa_nome=profilo.risorsa_tipo.value,
                    risorsa_corrente=player.risorsa_corrente,
                    costo_richiesto=profilo.costo_risorsa,
                    player=player.to_render_dict(),
                )
            eventi_turno.append(self._usa_abilita_speciale(player, mostro, profilo))

        elif azione == CombatAction.FUGGI:
            if random.random() < CHANCE_FUGA:
                self._log(f"{player.nome} e' fuggito dal combattimento.")
                self._termina_combattimento()
                return self._evento("fuga_riuscita", player=player.to_render_dict())
            eventi_turno.append({"tipo": "fuga_fallita"})

        if not mostro.is_vivo:
            return self._risolvi_vittoria_combattimento(eventi_turno)

        # Gestione fase e abilità speciale del Boss
        attacco_speciale_boss = False
        if mostro.is_boss:
            if not mostro.furia_attivata and mostro.hp_corrente <= (mostro.hp_max * 0.5):
                mostro.furia_attivata = True
                mostro.fase = 2
                mostro.attacco = int(round(mostro.attacco * 1.25))
                msg_furia = f"!!! {mostro.nome} entra nella FASE 2: Furia Draconica! Il suo potere distruttivo aumenta! !!!"
                self._log(msg_furia)
                eventi_turno.append({
                    "tipo": "fase_boss",
                    "fase": 2,
                    "nome": mostro.nome,
                    "messaggio": msg_furia,
                })

            if self.turni_combattimento % 3 == 0 or (mostro.fase == 2 and random.random() < 0.35):
                attacco_speciale_boss = True

        if attacco_speciale_boss:
            danno_grezzo = calcola_danno(mostro.attacco * 1.35, player.difesa_totale * 0.5)
            subito = player.subisci_danno(danno_grezzo)
            self._log(f"{mostro.nome} scatena {mostro.abilita_boss}! Infligge {subito} danni travolgenti a {player.nome}!")
            evento_mostro: Dict[str, Any] = {
                "tipo": "attacco_boss",
                "nome_abilita": mostro.abilita_boss,
                "danno": subito,
                "fase": mostro.fase,
            }
        else:
            subito = player.subisci_danno(calcola_danno(mostro.attacco, player.difesa_totale))
            self._log(f"{mostro.nome} infligge {subito} danni a {player.nome}.")
            evento_mostro = {"tipo": "attacco_mostro", "danno": subito}

        if player.classe == PlayerClass.GUERRIERO:
            evento_mostro["risorsa_guadagnata"] = player.guadagna_risorsa(FURIA_PER_DANNO_SUBITO)

        if player.classe == PlayerClass.CAVALIERE and player.effetti_attivi.get(EFFETTO_BALUARDO, 0) > 0:
            riflesso = mostro.subisci_danno(subito * BALUARDO_PERC_RIFLESSO)
            evento_mostro["contrattacco_baluardo"] = riflesso
            self._log(f"Il Baluardo Difensivo riflette {riflesso} danni su {mostro.nome}!")

        evento_mostro["player"] = player.to_render_dict()
        evento_mostro["mostro"] = mostro.to_render_dict()
        eventi_turno.append(evento_mostro)

        self._fine_turno_passivo(player)

        if not player.is_vivo:
            self.state = GameState.GAME_OVER
            self.mostro_corrente = None
            self._log(f"{player.nome} e' stato sconfitto...")
            return self._evento("game_over", eventi=eventi_turno, player=player.to_render_dict())

        if not mostro.is_vivo:
            return self._risolvi_vittoria_combattimento(eventi_turno)

        return self._evento(
            "turno_combattimento",
            eventi=eventi_turno,
            player=player.to_render_dict(),
            mostro=mostro.to_render_dict(),
        )

    def _usa_abilita_speciale(self, player: Player, mostro: Monster, profilo: ClassProfile) -> Dict[str, Any]:
        esito: Dict[str, Any] = {
            "tipo": "abilita_speciale",
            "nome_abilita": profilo.nome_abilita,
            "risorsa_nome": profilo.risorsa_tipo.value,
            "risorsa_consumata": player.consuma_risorsa(profilo.costo_risorsa),
        }

        if player.classe == PlayerClass.GUERRIERO:
            danno = calcola_danno(
                player.attacco_totale * COLPO_DEVASTANTE_MOLT,
                mostro.difesa * COLPO_DEVASTANTE_DIFESA,
            )
            esito["danno"] = mostro.subisci_danno(danno)
            self._log(f"{player.nome} scatena {profilo.nome_abilita}: {esito['danno']} danni a {mostro.nome}!")

        elif player.classe == PlayerClass.MAGO:
            esito["danno"] = mostro.subisci_danno(player.attacco_totale * DARDO_ARCANO_MOLT)
            self._log(f"{player.nome} scaglia {profilo.nome_abilita}: {esito['danno']} danni puri a {mostro.nome}!")

        elif player.classe == PlayerClass.CAVALIERE:
            player.effetti_attivi[EFFETTO_BALUARDO] = BALUARDO_DURATA_TURNI
            esito["buff_attivato"] = EFFETTO_BALUARDO
            esito["turni_buff"] = BALUARDO_DURATA_TURNI
            self._log(f"{player.nome} attiva {profilo.nome_abilita}: difesa aumentata per {BALUARDO_DURATA_TURNI} turni!")

        elif player.classe == PlayerClass.MEDICO:
            esito["hp_curati"] = player.cura(int(round(player.hp_max * PRONTO_SOCCORSO_PERC)))
            self._log(f"{player.nome} usa {profilo.nome_abilita} e recupera {esito['hp_curati']} HP.")

        esito["mostro"] = mostro.to_render_dict()
        esito["player"] = player.to_render_dict()
        return esito

    def _fine_turno_passivo(self, player: Player) -> None:
        if player.classe == PlayerClass.MAGO:
            player.guadagna_risorsa(REGEN_TURNO_MAGO)
        elif player.classe == PlayerClass.MEDICO:
            player.guadagna_risorsa(REGEN_TURNO_MEDICO)
        elif player.classe == PlayerClass.CAVALIERE:
            player.guadagna_risorsa(REGEN_TURNO_CAVALIERE)

        for nome_effetto in list(player.effetti_attivi):
            player.effetti_attivi[nome_effetto] -= 1
            if player.effetti_attivi[nome_effetto] <= 0:
                del player.effetti_attivi[nome_effetto]

    def _termina_combattimento(self) -> None:
        if self.player is not None:
            if self.player.classe == PlayerClass.GUERRIERO:
                self.player.risorsa_corrente = 0
            self.player.effetti_attivi.clear()
        self.mostro_corrente = None
        self.state = self._stato_prima_combattimento

    def _risolvi_vittoria_combattimento(self, eventi_turno: List[Dict[str, Any]]) -> Dict[str, Any]:
        assert self.player is not None and self.mostro_corrente is not None
        player = self.player
        mostro = self.mostro_corrente
        is_boss = mostro.is_boss

        self.mostri_sconfitti += 1
        self._log(f"{mostro.nome} e' stato sconfitto!")
        player.exp += mostro.exp_reward
        oro = random.randint(mostro.oro_min, mostro.oro_max) if mostro.oro_max > 0 else 0
        player.oro += oro

        drop = tira_drop(mostro.drop_table, mostro.drop_chance_totale)
        drop_raccolti: List[Item] = []
        drop_persi: List[Item] = []
        for oggetto in drop:
            if len(player.inventario) < player.max_inventario:
                player.aggiungi_oggetto(oggetto)
                drop_raccolti.append(oggetto)
                self._log(f"Hai ottenuto: {oggetto.nome} ({oggetto.rarita.value})")
            else:
                drop_persi.append(oggetto)
                self._log(
                    f"Inventario pieno ({player.max_inventario}/{player.max_inventario})! "
                    f"Hai dovuto lasciare a terra {oggetto.nome} ({oggetto.rarita.value})."
                )

        level_up = self._controlla_level_up()
        self._termina_combattimento()

        if is_boss:
            self.state = GameState.VITTORIA
            msg_vittoria = f"HAI SCONFITTO IL BOSS FINALE! {player.nome} ha trionfato sul {mostro.nome}!"
            self._log(msg_vittoria)
            return self._evento(
                "vittoria_finale",
                eventi=eventi_turno,
                mostro_sconfitto=mostro.to_render_dict(),
                exp_ottenuta=mostro.exp_reward,
                oro_ottenuto=oro,
                drop=[o.to_render_dict() for o in drop_raccolti],
                drop_persi=[o.to_render_dict() for o in drop_persi],
                level_up=level_up,
                player=player.to_render_dict(),
                statistiche={
                    "mostri_sconfitti": self.mostri_sconfitti,
                    "livello_raggiunto": player.livello,
                    "oro_totale": player.oro,
                    "turni_combattimento": self.turni_combattimento,
                    "hp_finali": f"{player.hp_corrente}/{player.hp_max}",
                    "classe": player.classe.value,
                },
                messaggio=msg_vittoria,
            )

        return self._evento(
            "vittoria_combattimento",
            eventi=eventi_turno,
            mostro_sconfitto=mostro.to_render_dict(),
            exp_ottenuta=mostro.exp_reward,
            oro_ottenuto=oro,
            drop=[o.to_render_dict() for o in drop_raccolti],
            drop_persi=[o.to_render_dict() for o in drop_persi],
            level_up=level_up,
            player=player.to_render_dict(),
        )

    def _usa_oggetto_in_combattimento(self, item: Item) -> Dict[str, Any]:
        assert self.player is not None
        player = self.player
        curato_hp = 0
        curata_risorsa = 0

        if item.cura_hp > 0:
            curato_hp = player.cura(item.cura_hp)
            self._log(f"{player.nome} usa {item.nome} e recupera {curato_hp} HP.")

        if item.cura_risorsa > 0:
            curata_risorsa = player.guadagna_risorsa(item.cura_risorsa)
            self._log(f"{player.nome} recupera {curata_risorsa} {player.risorsa_tipo.value}.")

        if item.consumabile:
            player.rimuovi_oggetto(item)

        return {
            "tipo": "uso_oggetto",
            "item": item.to_render_dict(),
            "hp_curati": curato_hp,
            "risorsa_curata": curata_risorsa,
            "player": player.to_render_dict(),
        }

    def _controlla_level_up(self) -> List[Dict[str, Any]]:
        assert self.player is not None
        player = self.player
        profilo = CLASS_PROFILES[player.classe]
        eventi: List[Dict[str, Any]] = []

        while player.exp >= exp_richiesta_per_livello(player.livello):
            player.exp -= exp_richiesta_per_livello(player.livello)
            player.livello += 1
            player.hp_max += profilo.delta_hp
            player.attacco_base += profilo.delta_attacco
            player.difesa_base += profilo.delta_difesa
            player.risorsa_max += profilo.delta_risorsa_max
            player.hp_corrente = player.hp_max
            player.risorsa_corrente = player.risorsa_max
            self._log(f"{player.nome} e' salito al livello {player.livello}!")
            eventi.append({
                "nuovo_livello": player.livello,
                "hp_max": player.hp_max,
                "attacco": player.attacco_base,
                "difesa": player.difesa_base,
                "risorsa_nome": player.risorsa_tipo.value,
                "risorsa_max": player.risorsa_max,
            })
        return eventi

    def apri_inventario(self) -> Dict[str, Any]:
        if self.player is None or self.state not in (GameState.ESPLORAZIONE, GameState.COMBATTIMENTO):
            return self._evento("errore", messaggio="Inventario non accessibile ora.")
        self._stato_prima_inventario = self.state
        self.state = GameState.INVENTARIO
        return self._evento(
            "apertura_inventario",
            oggetti=[i.to_render_dict() for i in self.player.inventario],
            player=self.player.to_render_dict(),
        )

    def chiudi_inventario(self) -> Dict[str, Any]:
        if self.state != GameState.INVENTARIO:
            return self._evento("errore", messaggio="L'inventario non e' aperto.")
        self.state = self._stato_prima_inventario
        return self._evento("chiusura_inventario")

    def equipaggia_oggetto(self, item: Item) -> Dict[str, Any]:
        if self.player is None or self.state != GameState.INVENTARIO:
            return self._evento("errore", messaggio="Apri l'inventario per equipaggiare un oggetto.")
        if item not in self.player.inventario:
            return self._evento("errore", messaggio="Oggetto non posseduto.")

        successo, precedente = self.player.equipaggia(item)
        if not successo:
            return self._evento("errore", messaggio=f"{item.nome} non e' equipaggiabile.")

        msg = f"Hai equipaggiato {item.nome}."
        if precedente is not None:
            msg += f" ({precedente.nome} e' tornato nell'inventario)"
        self._log(msg)

        return self._evento(
            "oggetto_equipaggiato",
            item=item.to_render_dict(),
            rimosso=precedente.to_render_dict() if precedente else None,
            player=self.player.to_render_dict(),
        )

    def disequipaggia_slot(self, slot: str) -> Dict[str, Any]:
        """Rimuove l'equipaggiamento dallo slot ('arma' o 'armatura')
        e lo rimette nell'inventario se c'e' spazio sufficiente."""
        if self.player is None:
            return self._evento("errore", messaggio="Nessun giocatore attivo.")
        if self.state not in (GameState.INVENTARIO, GameState.ESPLORAZIONE):
            return self._evento("errore", messaggio="Non puoi gestire l'equipaggiamento in questo momento.")

        successo, rimosso, msg = self.player.disequipaggia(slot)
        if not successo:
            return self._evento("errore", messaggio=msg)

        self._log(msg)
        return self._evento(
            "oggetto_disequipaggiato",
            slot=slot,
            item=rimosso.to_render_dict() if rimosso else None,
            messaggio=msg,
            player=self.player.to_render_dict(),
        )

    def scarta_oggetto(self, item: Item) -> Dict[str, Any]:
        """Rimuove definitivamente un oggetto dall'inventario."""
        if self.player is None:
            return self._evento("errore", messaggio="Nessun giocatore attivo.")
        if self.state not in (GameState.INVENTARIO, GameState.ESPLORAZIONE):
            return self._evento("errore", messaggio="Non puoi scartare oggetti in questo momento.")

        if item not in self.player.inventario:
            return self._evento("errore", messaggio="Oggetto non presente nell'inventario.")

        successo = self.player.scarta_oggetto(item)
        if not successo:
            return self._evento("errore", messaggio=f"Impossibile scartare {item.nome}.")

        msg = f"Hai scartato {item.nome}."
        self._log(msg)
        return self._evento(
            "oggetto_scartato",
            item=item.to_render_dict(),
            messaggio=msg,
            player=self.player.to_render_dict(),
        )

    def esiste_salvataggio(self, filepath: str = "savegame.json") -> bool:
        """Verifica se il file di salvataggio specificato esiste."""
        return os.path.isfile(filepath)

    def salva_partita(self, filepath: str = "savegame.json") -> Dict[str, Any]:
        """Serializza player, area_corrente, stato e log essenziali su file JSON."""
        if self.player is None:
            return self._evento("errore", messaggio="Nessuna partita attiva da salvare.")

        try:
            dati = {
                "player": self.player.to_dict(),
                "area_corrente": self.area_corrente.id if self.area_corrente else None,
                "state": self.state.name,
                "mostri_sconfitti": self.mostri_sconfitti,
                "turni_combattimento": self.turni_combattimento,
                "log": list(self.log[-20:]),
            }
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(dati, f, indent=2, ensure_ascii=False)

            msg = "Partita salvata con successo."
            self._log(msg)
            return self._evento(
                "salvataggio_completato",
                successo=True,
                messaggio=msg,
                filepath=filepath,
            )
        except Exception as e:
            return self._evento(
                "errore",
                messaggio=f"Impossibile salvare la partita: {e}",
            )

    def carica_partita(self, filepath: str = "savegame.json") -> Dict[str, Any]:
        """Legge il file JSON, ricostruisce il Player, ripristina l'area corrente
        e reimposta lo stato su GameState.ESPLORAZIONE."""
        if not self.esiste_salvataggio(filepath):
            return self._evento("errore", messaggio=f"File di salvataggio '{filepath}' non trovato.")

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                dati = json.load(f)

            self.player = Player.from_dict(dati["player"])

            area_id = dati.get("area_corrente")
            if area_id and area_id in self.aree:
                self.area_corrente = self.aree[area_id]
            else:
                self.area_corrente = self.aree.get("ingresso")

            self.mostro_corrente = None
            self.state = GameState.ESPLORAZIONE
            self.mostri_sconfitti = dati.get("mostri_sconfitti", 0)
            self.turni_combattimento = dati.get("turni_combattimento", 0)
            self.log = list(dati.get("log", []))
            self._log(f"Partita caricata: bentornato {self.player.nome}!")

            return self._evento(
                "caricamento_completato",
                successo=True,
                messaggio="Partita caricata con successo.",
                player=self.player.to_render_dict(),
                area=self.area_corrente.to_render_dict() if self.area_corrente else None,
            )
        except Exception as e:
            return self._evento(
                "errore",
                messaggio=f"Errore durante il caricamento del salvataggio: {e}",
            )


