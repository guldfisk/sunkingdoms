import itertools
import typing as t
from collections import defaultdict, OrderedDict

from eventtree.replaceevent import Event
from gameframe.connectioncontroller import ConnectionController
from gameframe.events import GameEvent
from gameframe.interface import GameInterface, Option
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


class _OptionSelectionContext(object):

    def __init__(self) -> None:
        self._started = False

    def _get_f_char(self):
        if self._started:
            return '│'
        else:
            self._started = True
            return '┌'

    def print(self, *args):
        print(self._get_f_char() + ' '.join(map(str, args)))

    def input(self, value: str = ''):
        return input(self._get_f_char() + value)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print('└')


class SKDummyInterface(GameInterface):

    def __init__(self, controller: ConnectionController):
        super().__init__(controller)
        self._running_events = 0

    def select_option(self, player: SKPlayer, options: t.Iterable[Option]) -> Option:
        _options = defaultdict(list)

        for option in options:
            _options[option.option_type].append(option)

        _options = OrderedDict(
            sorted(
                [
                    (key, sorted(value))
                    for key, value in
                    _options.items()
                ],
                key = lambda pair: pair[0]
            )
        )

        lines = OrderedDict(
            (
                key,
                key + ': ' + ', '.join(
                    option.value for option in values
                ),
            )
            for key, values in
            _options.items()
        )

        current_lines = lines.values()

        with _OptionSelectionContext() as context:
            while True:
                _max_line_len = max(*map(len, current_lines))
                context.print('┌' + '─' * _max_line_len + '┐')
                for ln in current_lines:
                    context.print('│' + ln.ljust(_max_line_len, ' ') + '│')
                context.print('└' + '─' * _max_line_len + '┘')

                user_input = context.input(': ')

                user_inputs = user_input.split('.')

                if len(user_inputs) > 1:
                    option_type_hint, user_input = user_inputs[:2]
                    limited_options = OrderedDict(
                        (key, value)
                        for key, value in
                        _options.items()
                        if option_type_hint in key.lower()
                    )
                else:
                    limited_options = _options

                option_hits = {
                    option
                    for option in
                    itertools.chain(
                        *limited_options.values()
                    )
                    if user_input in option.value.lower()
                }

                if len(option_hits) == 1:
                    return option_hits.__iter__().__next__()
                elif option_hits:
                    context.print('multiple options: ' + ', '.join(map(self.serialize_object, option_hits)))
                else:
                    context.print('no options')

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
        elif isinstance(o, Option):
            return f'{o.option_type}|{o.value}'
        else:
            return str(o)

    def serialize_event(self, event: Event, start: bool):
        if isinstance(event, GameEvent):
            return '{}{}{} {}'.format(
                self._running_events * '-|',
                '>' if start else '',
                event.__class__.__name__,
                {
                    key: self.serialize_object(value)
                    for key, value in
                    event.values.items()
                    if key in event.fields
                },
            )
        return '{}{}{} {}'.format(
            self._running_events * '-|',
            '>' if start else '',
            event.__class__.__name__,
            {
                key: self.serialize_object(value)
                for key, value in
                event.values.items()
                if key in event.values
            },
        )

    def notify_event_start(self, event: GameEvent):
        print(self.serialize_event(event, True))
        self._running_events += 1

    def notify_event_end(self, event: GameEvent):
        self._running_events -= 1
        print(self.serialize_event(event, False))
