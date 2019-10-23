from __future__ import annotations

import typing as t

from gameframe.events import GameEvent
from gameframe.game import Game
from gameframe.interface import GameInterface
from gameframe.setupinfo import SetupInfo
from sunkingdoms.artifacts import GameArtifact


class Zone(object):

    def __init__(
        self,
        ordered: bool,
        private: bool,
        face_up: bool,
        owner: t.Optional[Player] = None,
    ):
        self._ordered = ordered
        self._private = private
        self._face_up = face_up
        self._owner = owner

        self._cardboards: t.MutableSequence[Cardboard] = []

    def add_cardboard(self, cardboard: Cardboard) -> None:
        self._cardboards.append(cardboard)
        cardboard.zone = self

    def remove_cardboard(self, cardboard: Cardboard) -> None:
        self._cardboards.remove(cardboard)
        cardboard.zone = None

    @property
    def cards(self) -> t.MutableSequence[Cardboard]:
        return self._cardboards


class Price(object):
    pass


class Cardboard(GameArtifact):

    # def __init__(self):
    #     self._zone = None
    #     self._printed_card =

    @property
    def zone(self) -> Zone:
        return self._zone

    @zone.setter
    def zone(self, zone: Zone) -> None:
        self._zone = zone


class Card(GameArtifact):

    def on_play(self, event: GameEvent):
        pass

    def connect(self, event: GameEvent):
        pass

    def disconnect(self, event: GameEvent):
        pass


class Scout(object):

    def on_play(self, card: Card):
        pass


class Player(object):

    def __init__(self):
        self.money: int = 0
        self.life: int = 50
        self.damage: int = 0

        self._hand = Zone(
            ordered = False,
            private = True,
            face_up = True,
            owner = self,
        )
        self._battlefield = Zone(
            ordered = False,
            private = False,
            face_up = False,
            owner = self,
        )
        self._library = Zone(
            ordered = True,
            private = False,
            face_up = False,
            owner = self
        )
        self._discard_pile = Zone(
            ordered = False,
            private = False,
            face_up = True,
            owner = self,
        )

    @property
    def hand(self) -> Zone:
        return self._hand

    @property
    def battlefield(self) -> Zone:
        return self._battlefield


class SKSetup(SetupInfo):

    def __init__(self):
        pass


class SKGame(Game):

    def __init__(self, setup_info: SKSetup, interface: GameInterface):
        super().__init__(setup_info, interface)
        self._trade_deck = Zone(
            ordered = True,
            private = False,
            face_up = False,
        )
        self._trade_row = Zone(
            ordered = False,
            private = False,
            face_up = True,
        )

    def start(self):
        pass