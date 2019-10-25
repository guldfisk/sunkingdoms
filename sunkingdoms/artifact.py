import typing as t

from weakreflist import WeakList

from eventtree.replaceevent import Attributed, Condition, EventSession

from gameframe.events import GameEvent


class GameArtifact(Attributed):

    def __init__(self, game: EventSession, event: GameEvent):
        super().__init__(game)
        self._connected_conditions = WeakList()

    def create_condition(self, condition_type: t.Type[Condition], parent: GameEvent, **kwargs):
        self._connected_conditions.append(
            self._session.create_condition(
                condition_type = condition_type,
                parent = parent,
                source = self,
                **kwargs,
            )
        )

    def disconnect(self, parent: GameEvent):
        while self._connected_conditions:
            self._session.disconnect_condition(
                condition = self._connected_conditions.pop(-1)(),
                parent = parent,
            )
