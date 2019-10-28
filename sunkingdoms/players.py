import copy
import typing as t

from collections import defaultdict

from eventtree.replaceevent import ProtectedDynamicAttribute
from gameframe.game import Game
from gameframe.player import Player
from sunkingdoms.artifacts import Cardboard, Faction
from sunkingdoms.zones import Zone, ZoneOwner


class Battlefield(Zone[Cardboard]):

    def __init__(self, name: str, ordered: bool, private: bool, face_up: bool, owner: t.Optional[ZoneOwner] = None):
        super().__init__(name, ordered, private, face_up, owner)
        self._allegiance: t.Mapping[Faction, int] = defaultdict(int)

    @property
    def allegiance(self) -> t.Mapping[Faction, int]:
        return self._allegiance

    def leave(self, cardboard: Cardboard) -> None:
        super().leave(cardboard)
        for faction in cardboard.card.factions:
            self._allegiance[faction] -= 1

    def join(self, cardboard: Cardboard, index: t.Optional[int] = None) -> None:
        super().join(cardboard, index)
        for faction in cardboard.card.factions:
            self._allegiance[faction] += 1


class SKPlayer(ZoneOwner, Player):

    def __init__(self, game: Game):
        super().__init__(game)

        self.influence: int = 50
        self.money: int = 0
        self.damage: int = 0

        self.allegiance: ProtectedDynamicAttribute[t.Mapping[Faction, int]] = self.pda(
            'allegiance',
            lambda o: copy.copy(o.owner.battlefield.allegiance)
        )

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