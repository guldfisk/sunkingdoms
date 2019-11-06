from __future__ import annotations

from abc import abstractmethod

from ring import Ring

from gameframe.game import Game

from sunkingdoms.artifacts.artifacts import Cardboard
from sunkingdoms.players.interface import SKPlayer
from sunkingdoms.zones import Zone


class SKGame(Game):
    players: Ring[SKPlayer]
    trade_deck: Zone[Cardboard]
    trade_row: Zone[Cardboard]
    scrap_pile: Zone[Cardboard]

    @abstractmethod
    def start(self):
        pass

