from __future__ import annotations

import typing as t

from gameframe.events import GameEvent
from sunkingdoms.artifacts import Card, Price, Cardboard, Actions, Action, Faction
from sunkingdoms import events as e


class AllyAction(Action):

    def __init__(self, text: str, faction: Faction, result: t.Callable[[e.ActivateAction], None], requirement: int = 1):
        super().__init__(text)
        self._faction = faction
        self._result = result
        self._requirement = requirement + 1

    def requirements_fulfilled(self, event: e.SKGameEvent) -> bool:
        return event.player.allegiance.get()[self._faction] >= self._requirement

    def do(self, event: e.ActivateAction):
        self._result(event)


class Scout(Card):
    name = 'Scout'
    price = Price(0)

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 1)


class Viper(Card):
    name = 'viper'
    price = Price(0)

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddDamage, amount = 1)


class FederationShuttle(Card):
    name = 'Federation Shuttle'
    price = Price(1)
    factions = frozenset((Faction.BLUE, ))

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                AllyAction(
                    'Gain 4 influence',
                    Faction.BLUE,
                    self._gain_influence,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 2)

    @classmethod
    def _gain_influence(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.GainInfluence, amount = 4)