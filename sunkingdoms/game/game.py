from __future__ import annotations

import typing as t

from ring import Ring

from gameframe.events import GameEvent
from gameframe.interface import GameInterface

from sunkingdoms.artifacts.artifacts import Cardboard
from sunkingdoms.players.player import SKPlayer
from sunkingdoms.setup import SKSetup
from sunkingdoms.signatures import SKPlayerSignature
from sunkingdoms.zones import Zone
from sunkingdoms.game.interface import SKGame as SKGameInterface


class SKGame(SKGameInterface):

    def __init__(self, setup_info: SKSetup, interface: GameInterface, signatures: t.Collection[SKPlayerSignature]):
        super().__init__(setup_info, interface, signatures)

        self._players = Ring(
            SKPlayer(self, signature)
            for signature in
            signatures
        )

        self._trade_deck = Zone(
            'trade deck',
            ordered = True,
            private = False,
            face_up = False,
        )
        self._trade_row = Zone(
            'trade row',
            ordered = False,
            private = False,
            face_up = True,
        )
        self._scrap_pile = Zone(
            'scrap',
            ordered = False,
            private = False,
            face_up = True,
        )

    @property
    def players(self) -> Ring[SKPlayer]:
        return self._players

    def log_event(self, event: GameEvent) -> None:
        self._interface.notify_event_start(event)

    def event_finished(self, event: GameEvent, success: bool) -> None:
        self._interface.notify_event_end(event, success)

    @property
    def trade_deck(self) -> Zone[Cardboard]:
        return self._trade_deck

    @property
    def trade_row(self) -> Zone[Cardboard]:
        return self._trade_row

    @property
    def scrap_pile(self) -> Zone[Cardboard]:
        return self._scrap_pile

    def start(self):
        pass