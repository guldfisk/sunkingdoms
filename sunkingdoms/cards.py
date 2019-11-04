from __future__ import annotations

import typing as t

from eventtree import replaceevent as rev
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
                    self._action,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 2)

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.GainInfluence, amount = 4)


class Cutter(Card):
    name = 'Cutter'
    price = Price(2)
    factions = frozenset((Faction.BLUE, ))

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                AllyAction(
                    'Gain 4 damage',
                    Faction.BLUE,
                    self._action,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 2)
        event.spawn_tree(e.GainInfluence, amount = 4)

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.AddDamage, amount = 4)


class TopdeckNextShipBought(rev.ContinuousDelayedReplacement):
    trigger = 'BuyCardboard'
    terminate_trigger = 'TakeTurn'

    def _replace(self, event: e.BuyCardboard):
        event.replace_clone(to=event.player.library)


class Freighter(Card):
    name = 'Freighter'
    price = Price(4)
    factions = frozenset((Faction.BLUE, ))

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                AllyAction(
                    'Topdeck next ship',
                    Faction.BLUE,
                    self._action,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 4)

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.game.create_condition(TopdeckNextShipBought)