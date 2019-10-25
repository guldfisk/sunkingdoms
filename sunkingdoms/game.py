from __future__ import annotations

import random
import typing as t

from gameframe.events import GameEvent
from gameframe.game import Game
from gameframe.interface import GameInterface
from ring import Ring
from sunkingdoms.artifacts import Cardboard
from sunkingdoms.players import SKPlayer
from sunkingdoms.setup import SKSetup
from sunkingdoms.zones import Zone


class SKGame(Game):

    def __init__(self, setup_info: SKSetup, interface: GameInterface):
        super().__init__(setup_info, interface)

        self._players = Ring(
            SKPlayer()
            for _ in
            range(setup_info.player_count)
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

    @property
    def players(self) -> Ring[SKPlayer]:
        return self._players

    def log_event(self, event: GameEvent) -> None:
        self._interface.notify_event_start(event)

    def event_finished(self, event: GameEvent) -> None:
        self._interface.notify_event_end(event)

    @property
    def trade_deck(self) -> Zone[Cardboard]:
        return self._trade_deck

    @property
    def trade_row(self) -> Zone[Cardboard]:
        return self._trade_row

    def start(self):
        pass