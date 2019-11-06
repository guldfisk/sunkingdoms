from __future__ import annotations

import typing as t
from abc import abstractmethod
from enum import Enum

from eventtree.replaceevent import EventSession
from gameframe.events import GameEvent
from sunkingdoms.artifacts.artifact import GameArtifact
from sunkingdoms.attack import Target
from sunkingdoms.zones import Zoneable, Zone


class Price(object):

    def __init__(self, amount: int):
        self._amount = amount

    @property
    def amount(self) -> int:
        return self._amount


class Cardboard(Zoneable, Target):

    def __init__(self, game: EventSession, event: GameEvent, card_type: t.Type[Card]):
        super().__init__(game, event)
        self._printed_card_type = card_type
        self._card = card_type(self, event)
        self._zone = None

    def attack(self, damage: int, event: GameEvent):
        self._card.attack(damage, event)

    @property
    def card(self) -> Card:
        return self._card

    @property
    def zone(self) -> Zone:
        return self._zone

    @zone.setter
    def zone(self, zone: Zone) -> None:
        self._zone = zone


class Action(object):

    def __init__(self, text: str):
        self._exhausted = False
        self._text = text

    @property
    def text(self) -> str:
        return self._text

    def exhaust(self) -> None:
        self._exhausted = True

    def refresh(self) -> None:
        self._exhausted = False

    def requirements_fulfilled(self, event: GameEvent) -> bool:
        pass

    def available(self, event: GameEvent) -> bool:
        return not self._exhausted and self.requirements_fulfilled(event)

    def cost(self, event: GameEvent):
        pass

    def do(self, event: GameEvent):
        pass

    def __repr__(self):
        return self.text


class Actions(object):

    def __init__(self, actions: t.Iterable[Action]):
        self._actions = list(actions)

    def __iter__(self) -> t.Iterator[Action]:
        return self._actions.__iter__()

    def refresh(self) -> None:
        for action in self._actions:
            action.refresh()


class Faction(Enum):
    YELLOW = 'yellow'
    BLUE = 'blue'
    RED = 'red'
    GREEN = 'green'


class CardType(Enum):
    SHIP = 'ship'
    BASE = 'base'


class Card(object):
    name: str
    price: Price
    factions: t.FrozenSet[Faction] = frozenset()
    card_type: CardType = CardType.SHIP

    health: int = 0
    outpost: bool = False

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        self._cardboard = cardboard
        self._actions = Actions(())

    def on_play(self, event: GameEvent):
        pass

    def attack(self, damage: int, event: GameEvent):
        pass

    @property
    def actions(self) -> Actions:
        return self._actions
