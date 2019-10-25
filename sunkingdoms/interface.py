import typing as t

from gameframe.connectioncontroller import ConnectionController
from gameframe.events import GameEvent
from gameframe.interface import GameInterface
from gameframe.signature import PlayerSignature
from sunkingdoms.artifacts import Zone, Cardboard
from sunkingdoms.players import SKPlayer


class SKPlayerSignature(PlayerSignature):

    def __init__(self, name: str):
        self._name = name

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._name == other._name
        )


class SKDummyController(ConnectionController):
    pass


class SKDummyInterface(GameInterface):

    def __init__(self, controller: ConnectionController):
        super().__init__(controller)
        self._running_events = 0

    def select_option(self, player: SKPlayer, options: t.Iterable[t.Any]) -> t.Any:
        options = list(options)
        while True:
            print(', '.join(map(self.serialize_object, player.hand)))
            print(', '.join(map(self.serialize_object, options)))
            index = input(': ')
            try:
                index = int(index)
            except ValueError:
                continue
            if index >= len(options):
                continue
            return options[index]

    @classmethod
    def serialize_object(cls, o: t.Any):
        if isinstance(o, type):
            return o.__name__
        elif isinstance(o, Zone):
            return o.name
        elif isinstance(o, Cardboard):
            return o.card.name
        elif isinstance(o, SKPlayer):
            return 'player'
        else:
            return str(o)

    def serialize_event(self, event: GameEvent, start: bool):
        return '{}{}{} {}'.format(
            self._running_events * '-|',
            '>' if start else '',
            event.__class__.__name__,
            {
                key: self.serialize_object(value)
                for key, value in
                event.values.items()
            },
        )

    def notify_event_start(self, event: GameEvent):
        print(self.serialize_event(event, True))
        self._running_events += 1

    def notify_event_end(self, event: GameEvent):
        self._running_events -= 1

        print(self.serialize_event(event, False))

