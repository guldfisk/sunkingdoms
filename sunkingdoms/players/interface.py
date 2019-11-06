from __future__ import annotations

import typing as t

from abc import abstractmethod

from yeetlong.multiset import Multiset

from gameframe.player import Player
from gameframe.events import GameEvent

from sunkingdoms.attack import Target
from sunkingdoms.artifacts.artifacts import Cardboard, Faction
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


class SKPlayer(ZoneOwner, Player, Target):
    allegiance: Multiset[Faction]
    get_legal_targets: t.Callable[[int], t.Iterable[Target]]
    hand: Zone[Cardboard]
    battlefield: Battlefield
    library: Zone[Cardboard]
    discard_pile: Zone[Cardboard]
    influence: int
    money: int
    damage: int
    opponent: SKPlayer

    @abstractmethod
    def attack(self, damage: int, event: GameEvent):
        pass
