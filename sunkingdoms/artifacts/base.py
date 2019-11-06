from __future__ import annotations

from sunkingdoms.artifacts.artifacts import CardType, Card

from sunkingdoms import events as e


class Base(Card):
    card_type = CardType.BASE

    def attack(self, damage: int, event: e.Attack):
        if damage >= self.health:
            event.spawn_tree(
                e.DestroyCardboard,
                target = self._cardboard,
                frm = self._cardboard.zone,
                to = self._cardboard.zone.owner.discard_pile,
            )
