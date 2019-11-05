import copy
import typing as t

from yeetlong.multiset import Multiset

from eventtree.replaceevent import EventProperty

from gameframe.game import Game
from gameframe.player import Player
from sunkingdoms.artifacts import Cardboard, Faction
from sunkingdoms.zones import Zone, ZoneOwner


class Battlefield(Zone[Cardboard]):

    def __init__(self, name: str, ordered: bool, private: bool, face_up: bool, owner: t.Optional[ZoneOwner] = None):
        super().__init__(name, ordered, private, face_up, owner)
        self._allegiance: Multiset[Faction] = Multiset()

    @property
    def allegiance(self) -> Multiset[Faction]:
        return self._allegiance

    def leave(self, cardboard: Cardboard) -> None:
        super().leave(cardboard)
        self._allegiance -= cardboard.card.factions

    def join(self, cardboard: Cardboard, index: t.Optional[int] = None) -> None:
        super().join(cardboard, index)
        self._allegiance += cardboard.card.factions


class SKPlayer(ZoneOwner, Player):
    allegiance: Multiset[Faction]

    def __init__(self, game: Game):
        super().__init__(game)

        self.influence: int = 50
        self.money: int = 0
        self.damage: int = 0

        self._hand = Zone(
            name = 'hand',
            ordered = False,
            private = True,
            face_up = True,
            owner = self,
        )
        self._battlefield = Battlefield(
            name = 'battlefield',
            ordered = False,
            private = False,
            face_up = False,
            owner = self,
        )
        self._library = Zone(
            name = 'library',
            ordered = True,
            private = False,
            face_up = False,
            owner = self
        )
        self._discard_pile = Zone(
            name = 'discard',
            ordered = False,
            private = False,
            face_up = True,
            owner = self,
        )

    @EventProperty
    def allegiance(self) -> Multiset[Faction]:
        return copy.copy(self.battlefield.allegiance)

    @property
    def hand(self) -> Zone[Cardboard]:
        return self._hand

    @property
    def battlefield(self) -> Battlefield:
        return self._battlefield

    @property
    def library(self) -> Zone[Cardboard]:
        return self._library

    @property
    def discard_pile(self) -> Zone[Cardboard]:
        return self._discard_pile