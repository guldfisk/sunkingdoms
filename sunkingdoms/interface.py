import copy
import itertools
import typing as t
from collections import defaultdict, OrderedDict
from enum import Enum

from eventtree.replaceevent import Event
from gameframe.connectioncontroller import ConnectionController
from gameframe.events import GameEvent
from gameframe.interface import GameInterface, Option, O
from gameframe.signature import PlayerSignature
from sunkingdoms.artifacts import Zone, Cardboard
from sunkingdoms.events import TakeTurn
from sunkingdoms.players import SKPlayer
from yeetlong.multiset import Multiset


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

    def __init__(self, player: SKPlayer) -> None:
        self._player = player
        self._started = False
        self._values = []
        self._current_line_length = 0

    def _get_f_char(self):
        if self._started:
            return '│'
        else:
            self._started = True
            return '┌'

    def print(self, *args, ignore_values: bool = False):
        p_value = self._get_f_char() + ' '.join(map(str, args))
        if len(p_value) > self._current_line_length:
            self._current_line_length = len(p_value)
        if self._values and not ignore_values:
            p_value += ' ' + self._values.pop(0)
        print(p_value)

    def input(self, value: str = ''):
        return input(self._get_f_char() + value)

    def __enter__(self):
        self._values.extend(
            [
                f'money: {self._player.money}, damage: {self._player.damage}, influence: {self._player.influence}',
                'hand         : ' + count_zone(self._player.hand),
                'battlefield  : ' + count_zone(self._player.battlefield),
                'discard pile : ' + count_zone(self._player.discard_pile),
                'library      : ' + count_zone(self._player.library),
            ]
        )

        return self

    def flush(self):
        for value in self._values:
            print('│ '.ljust(self._current_line_length + 1, ' ') + value)
        self._values[:] = []

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush()
        print('└')


def count_zone(zone: Zone) -> str:
    return ', '.join(
        (
            (str(multiplicity) + 'x ')
            if multiplicity > 1 else
            ''
        ) + name
        for name, multiplicity in
        sorted(
            Multiset(
                map(serialize_object, zone)
            ).items(),
            key = lambda vs: vs[0],
        )
    )


def serialize_object(o: t.Any):
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


class SKDummyInterface(GameInterface):

    class EventStatus(Enum):
        START = ''
        SUCCESS = '>'
        FAIL = '!>'


    def __init__(self, controller: ConnectionController):
        super().__init__(controller)
        self._running_events = 0
        self._turn_counter = 0

        self._pending_selections: Multiset[Option] = Multiset()

    def _select_with_context(
        self,
        options: t.Mapping[str, t.List[Option]],
        context: _OptionSelectionContext
    ) -> Option:
        lines = [
            key + ': ' + ', '.join(
                option.value for option in values
            )
            for key, values in
            options.items()
        ]

        while True:
            _max_line_len = max(0, *map(len, lines))
            context.print('┌' + '─' * _max_line_len + '┐')
            for ln in lines:
                context.print('│' + ln.ljust(_max_line_len, ' ') + '│')
            context.print('└' + '─' * _max_line_len + '┘')

            context.flush()

            user_input = context.input(': ')

            if not user_input and 'pass turn' in options:
                return options['pass turn'][0]

            if user_input == 'a' and 'activate cardboard' in options:
                self._pending_selections = Multiset(options['activate cardboard'][1:])
                return options['activate cardboard'][0]

            if user_input == 'p' and 'play card' in options:
                self._pending_selections = Multiset(options['play card'][1:])
                return options['play card'][0]

            user_inputs = user_input.split('.')

            if len(user_inputs) > 1:
                option_type_hint, user_input = user_inputs[:2]
                limited_options = OrderedDict(
                    (key, value)
                    for key, value in
                    options.items()
                    if option_type_hint in key.lower()
                )
            else:
                limited_options = options

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
                context.print('multiple options: ' + ', '.join(map(serialize_object, option_hits)))
            else:
                context.print('no options')

    def _select_option(
        self,
        player: SKPlayer,
        options: t.Iterable[Option],
        context: t.Optional[_OptionSelectionContext] = None,
    ) -> Option:
        if self._pending_selections:
            _options = Multiset(options)
            intersection = self._pending_selections & _options
            if intersection:
                option = intersection.__iter__().__next__()
                self._pending_selections.remove(option, 1)
                return (_option for _option in _options if _option == option).__iter__().__next__()
            else:
                self._pending_selections.clear()

        options = list(options)

        if len(options) == 1:
            return options[0]

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

        if context is None:
            with _OptionSelectionContext(player) as context:
                return self._select_with_context(
                    _options,
                    context,
                )
        else:
            return self._select_with_context(_options, context)

    def select_option(self, player: SKPlayer, options: t.Iterable[O]) -> O:
        return self._select_option(player, options)

    def select_options(
        self,
        player: SKPlayer,
        options: t.Iterable[O],
        minimum: int = 0,
        maximum: t.Optional[int] = None,
    ) -> t.Iterable[O]:

        finished_option = Option('selection control', 'done')
        reset_option = Option('selection control', 'reset')

        options = list(options)

        selected = []
        remaining = copy.copy(options)

        with _OptionSelectionContext(player) as context:
            context.print(
                f'Select from {minimum} to {len(options) if maximum is None else maximum}',
                ignore_values = True,
            )

            while remaining and (maximum is None or len(selected) < maximum):
                _options = copy.copy(remaining)

                if len(selected) >= minimum:
                    _options.append(finished_option)

                _options.append(reset_option)

                context.print('selected: ' + ', '.join(map(serialize_object, selected)), ignore_values = True)

                option = self._select_option(player, _options, context)

                if option == finished_option:
                    break

                if option == reset_option:
                    selected[:] = []
                    remaining = copy.copy(options)
                    continue

                selected.append(option)
                remaining.remove(option)

        return selected

    def serialize_event(self, event: Event, status: EventStatus):
        if isinstance(event, GameEvent):
            if status == self.EventStatus.START and isinstance(event, TakeTurn):
                print('-' * 30 + 'Turn: ' + str(self._turn_counter) + '-' * 30)
                self._turn_counter += 1
            return '{}{}{} {}'.format(
                self._running_events * '-|',
                status.value,
                event.__class__.__name__,
                {
                    key: serialize_object(value)
                    for key, value in
                    event.values.items()
                    if key in event.fields
                },
            )
        return '{}{}{} {}'.format(
            self._running_events * '-|',
            status.value,
            event.__class__.__name__,
            {
                key: serialize_object(value)
                for key, value in
                event.values.items()
                if key in event.values
            },
        )

    def notify_event_start(self, event: GameEvent) -> None:
        print(self.serialize_event(event, self.EventStatus.START))
        self._running_events += 1

    def notify_event_end(self, event: GameEvent, success: bool) -> None:
        self._running_events -= 1
        print(self.serialize_event(event, self.EventStatus.SUCCESS if success else self.EventStatus.FAIL))
