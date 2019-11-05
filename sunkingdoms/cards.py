from __future__ import annotations

import typing as t

from eventtree import replaceevent as rev
from eventtree.replaceevent import StaticAttributeModification, Event, T
from gameframe.events import GameEvent
from gameframe.interface import Option
from sunkingdoms.artifacts import Card, Price, Cardboard, Actions, Action, Faction, Base
from sunkingdoms import events as e
from sunkingdoms.players import SKPlayer
from yeetlong.multiset import Multiset


class AllyAction(Action):

    def __init__(self, text: str, faction: Faction, result: t.Callable[[e.ActivateAction], None], requirement: int = 1):
        super().__init__(text)
        self._faction = faction
        self._result = result
        self._requirement = requirement + 1

    def requirements_fulfilled(self, event: e.SKGameEvent) -> bool:
        return event.player.allegiance[self._faction] >= self._requirement

    def do(self, event: e.ActivateAction):
        self._result(event)


class FreeAction(Action):

    def __init__(self, text: str, result: t.Callable[[e.ActivateAction], None]):
        super().__init__(text)
        self._result = result

    def requirements_fulfilled(self, event: e.SKGameEvent) -> bool:
        return True

    def do(self, event: e.ActivateAction):
        self._result(event)


class ScrapAction(Action):

    def __init__(self, text: str, result: t.Callable[[e.ActivateAction], None]):
        super().__init__(text)
        self._result = result

    def requirements_fulfilled(self, event: e.SKGameEvent) -> bool:
        return True

    def cost(self, event: e.ActivateAction):
        event.spawn_tree(e.ScrapCardboard, frm=event.target.zone)

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


class TradePod(Card):
    name = 'Trade Pod'
    price = Price(2)
    factions = frozenset((Faction.GREEN, ))

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                AllyAction(
                    'Add 2 damage',
                    Faction.GREEN,
                    self._action,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddMoney, amount = 3)

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.AddDamage, amount = 2)


class BlobFighter(Card):
    name = 'BlobFighter'
    price = Price(1)
    factions = frozenset((Faction.GREEN, ))

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                AllyAction(
                    'Draw 1 card',
                    Faction.GREEN,
                    self._action,
                ),
            )
        )

    def on_play(self, event: GameEvent):
        event.spawn_tree(e.AddDamage, amount = 3)

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.DrawCardboards, amount = 1)


class WarningBeacon(Base):
    name = 'Warning Beacon'
    price = Price(3)
    factions = frozenset((Faction.RED,))
    health = 3
    outpost = True

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                ScrapAction(
                    'scrap: 5 damage',
                    self._action,
                ),
            )
        )

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        event.spawn_tree(e.AddDamage, amount = 5)


class RecyclingStation(Base):
    name = 'Recycling Station'
    price = 4
    factions = frozenset((Faction.YELLOW,))
    health = 4
    outpost = True

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._actions = Actions(
            (
                FreeAction(
                    'Gain 1 money or loot 2',
                    self._action,
                ),
            )
        )

    @classmethod
    def _action(cls, event: e.ActivateAction) -> None:
        mode = event.game.interface.select_string(
            event.player,
            'select mode',
            ('plus coin', 'loot'),
        )
        if mode == 'plus coin':
            event.spawn_tree(e.AddMoney, amount = 1)
        else:
            cardboards: t.List[Cardboard] = [
                option.item
                for option in
                event.game.interface.select_options(
                    event.player,
                    (
                        Option(
                            'Choose discard',
                            cardboard.card.name,
                            item = cardboard,
                        )
                        for cardboard in
                        event.player.hand
                    ),
                    minimum = 0,
                    maximum = 2,
                )
            ]
            for cardboard in cardboards:
                event.spawn_tree(e.DiscardCardboard, target = cardboard)

            event.spawn_tree(e.DrawCardboards, amount = len(cardboards))


class MechWorld(Base):
    name = 'Mech World'
    price = 5
    factions = frozenset((Faction.RED,))
    health = 6
    outpost = True

    def __init__(self, cardboard: Cardboard, event: GameEvent):
        super().__init__(cardboard, event)
        self._cardboard.create_condition(
            self.FactionBonus,
            event,
        )

    class FactionBonus(StaticAttributeModification[Multiset[Faction]]):
        trigger = 'allegiance'
        source: Cardboard

        def condition(self, source: t.Any, owner: SKPlayer, value: Multiset[Faction], **kwargs) -> bool:
            return owner == self.source.zone.owner and self.source in self.source.zone.owner.battlefield

        def resolve(self, owner: SKPlayer, value: Multiset[Faction]) -> Multiset[Faction]:
            return value + (set(Faction.__iter__()) - self.source.card.factions)
