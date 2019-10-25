from gameframe.player import Player
from sunkingdoms.artifacts import Cardboard
from sunkingdoms.zones import Zone, ZoneOwner


class SKPlayer(ZoneOwner, Player):

    def __init__(self):
        self.money: int = 0
        self.life: int = 50
        self.damage: int = 0

        self._hand = Zone(
            name = 'hand',
            ordered = False,
            private = True,
            face_up = True,
            owner = self,
        )
        self._battlefield = Zone(
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
    def battlefield(self) -> Zone[Cardboard]:
        return self._battlefield

    @property
    def library(self) -> Zone[Cardboard]:
        return self._library

    @property
    def discard_pile(self) -> Zone[Cardboard]:
        return self._discard_pile