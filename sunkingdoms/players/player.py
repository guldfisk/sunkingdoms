from __future__ import annotations

import copy
import typing as t

from yeetlong.multiset import Multiset

from eventtree.replaceevent import EventProperty

from gameframe.events import GameEvent

from sunkingdoms.artifacts.artifacts import Cardboard, Faction, CardType
from sunkingdoms.zones import Zone
from sunkingdoms import events as e
from sunkingdoms.attack import Target
from sunkingdoms.players.interface import SKPlayer as SKPlayerInterface, Battlefield
from sunkingdoms.signatures import SKPlayerSignature
from sunkingdoms.game.interface import SKGame



class SKPlayer(SKPlayerInterface):
    _session: SKGame

    def __init__(self, game: SKGame, signature: SKPlayerSignature):
        super().__init__(game, signature)

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

    @property
    def opponent(self) -> SKPlayer:
        return self._session.players.after(self)

    @property
    def signature(self) -> SKPlayerSignature:
        return self._signature

    def attack(self, damage: int, event: GameEvent) -> None:
        event.spawn_tree(e.LoseInfluence, player = self, amount = damage)

    @EventProperty
    def allegiance(self) -> Multiset[Faction]:
        return copy.copy(self.battlefield.allegiance)

    def get_legal_targets(self, available_damage: int) -> t.List[Target]:
        bases = [cardboard for cardboard in self.battlefield if cardboard.card.card_type == CardType.BASE]
        outposts = [base for base in bases if base.card.outpost]
        if outposts:
            return [outpost for outpost in outposts if outpost.card.health <= available_damage]
        return [self] + [base for base in bases if base.card.health <= available_damage]

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
