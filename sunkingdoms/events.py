import typing as t
from abc import abstractmethod

from eventtree.replaceevent import EventCheckException, EventResolutionException
from gameframe.events import GameEvent
from sunkingdoms.artifacts import Card, Cardboard
from sunkingdoms import cards
from sunkingdoms.game import Zone, SKSetup, SKGame
from sunkingdoms.players import SKPlayer


class SKGameEvent(GameEvent):

    @property
    def game(self) -> SKGame:
        return self._session

    @property
    def player(self) -> t.Optional[SKPlayer]:
        return self._values['player']

    @abstractmethod
    def payload(self, **kwargs):
        pass

    def serialize(self) -> t.Any:
        pass

    def deserialize(self, s: t.Any) -> GameEvent:
        pass


class CreateCardboard(SKGameEvent):

    @property
    def to(self) -> Zone:
        return self._values['to']

    @to.setter
    def to(self, zone: Zone) -> None:
        self._values['to'] = zone

    @property
    def card_type(self) -> t.Type[Card]:
        return self._values['card_type']

    @card_type.setter
    def card_type(self, card_type: t.Type[Card]) -> None:
        self._values['card_type'] = card_type

    @property
    def face_up(self) -> bool:
        return self._values['face_up']

    @face_up.setter
    def face_up(self, face_up: bool) -> None:
        self._values['face_up'] = face_up

    def setup(self, **kwargs):
        self._values.setdefault('face_up', None)

    def payload(self, **kwargs):
        self.to.join(
            Cardboard(
                game = self._session,
                card_type = self.card_type,
                event = self,
            )
        )


class MoveCardboard(SKGameEvent):

    @property
    def target(self) -> Cardboard:
        return self._values['target']

    @target.setter
    def target(self, zoneable: Cardboard) -> None:
        self._values['target'] = zoneable

    @property
    def frm(self) -> Zone:
        return self._values['frm']

    @frm.setter
    def frm(self, zone: Zone) -> None:
        self._values['frm'] = zone

    @property
    def to(self) -> Zone:
        return self._values['to']

    @to.setter
    def to(self, zone: Zone) -> None:
        self._values['to'] = zone

    @property
    def index(self) -> int:
        return self._values['index']

    @index.setter
    def index(self, value: int) -> None:
        self._values['index'] = value

    def setup(self, **kwargs):
        self._values.setdefault('index', None)

    def check(self, **kwargs):
        if not self.target in self.frm:
            raise EventCheckException()

    def payload(self, **kwargs):
        self.to.join(self.target)
        return self.target
    
    
class Reshuffle(SKGameEvent):

    # def setup(self, **kwargs):
    #     self._values.setdefault('to', self.player)

    def payload(self, **kwargs):
        if self.player.library:
            index = len(self.player.graveyard)
            for cardboard in tuple(self.player.graveyard):
                self.spawn_tree(
                    MoveCardboard,
                    frm=self.player.graveyard,
                    to=self.player.library,
                    target=cardboard,
                    index = 0,
                )
            self.spawn_tree(ShuffleZone, to = self.player.library, index = index)
        else:
            for cardboard in tuple(self.player.discard_pile):
                self.spawn_tree(
                    MoveCardboard,
                    frm = self.player.discard_pile,
                    to = self.player.library,
                    target = cardboard,
                )
            self.spawn_tree(ShuffleZone, to = self.player.library)
    
    
class DrawCardboard(SKGameEvent):

    def payload(self, **kwargs):
        if not self.player.library:
            self.spawn_tree(Reshuffle)
        if not self.player.library:
            raise EventResolutionException()
        return self.depend_tree(
            MoveCardboard,
            frm = self.player.library,
            to = self.player.hand,
            target = self.player.library[-1],
        )


class DrawCardboards(SKGameEvent):

    @property
    def amount(self) -> int:
        return self._values['amount']

    @amount.setter
    def amount(self, value: int) -> None:
        self._values['amount'] = value

    def payload(self, **kwargs):
        cardboards = []
        for _ in range(self.amount):
            cardboard = self.spawn_tree(DrawCardboard)
            if cardboard is None:
                break
            cardboards.append(cardboard)
        return cardboards
    
    
class DrawHand(SKGameEvent):

    @property
    def amount(self) -> int:
        return self._values['amount']

    @amount.setter
    def amount(self, value: int) -> None:
        self._values['amount'] = value

    def setup(self, **kwargs):
        self._values.setdefault('amount', 5)

    def payload(self, **kwargs):
        return self.depend_tree(DrawCardboards)


class RefillTradeRow(SKGameEvent):

    @property
    def target(self) -> Cardboard:
        return self._values['target']

    @target.setter
    def target(self, cardboard: Cardboard) -> None:
        self._values['target'] = cardboard

    @property
    def frm(self) -> Zone:
        return self._values['frm']

    @property
    def to(self) -> Zone:
        return self._values['to']

    @to.setter
    def to(self, zone: Zone) -> None:
        self._values['to'] = zone

    def setup(self, **kwargs):
        self._values.setdefault('to', self.game.trade_row)
        self._values.setdefault('frm', self.game.trade_deck)
        self._values.setdefault('target', self.game.trade_deck[-1])

    def payload(self, **kwargs):
        return self.depend_tree(MoveCardboard)


class ShuffleZone(SKGameEvent):

    @property
    def to(self) -> Zone:
        return self._values['to']

    @to.setter
    def to(self, zone: Zone) -> None:
        self._values['to'] = zone

    def payload(self, **kwargs):
        self.to.shuffle()


class SetupGame(SKGameEvent):

    @property
    def setup_info(self) -> SKSetup:
        return self._values['setup_info']

    def payload(self, **kwargs):
        for _ in range(10):
            self.spawn_tree(
                CreateCardboard,
                card_type = cards.FederationShuttle,
                to = self.game.trade_deck,
            )
        self.spawn_tree(ShuffleZone, to = self.game.trade_deck)
        for _ in range(5):
            self.spawn_tree(RefillTradeRow)
        for player in self.game.players.all:
            for _ in range(8):
                self.spawn_tree(
                    CreateCardboard,
                    card_type = cards.Scout,
                    to = player.discard_pile,
                )
            for _ in range(2):
                self.spawn_tree(
                    CreateCardboard,
                    card_type = cards.Viper,
                    to = player.discard_pile,
                )
        for player in self.game.players.all:
            self.spawn_tree(DrawHand, player = player)


class TakeTurn(SKGameEvent):

    @property
    def player(self) -> SKPlayer:
        return self._values['player']

    def payload(self, **kwargs):
        self.game.interface.select_option(self.player, list(range(3)))


class PlayGame(SKGameEvent):

    @property
    def setup_info(self) -> SKSetup:
        return self._values['setup_info']

    def payload(self, **kwargs):
        self.spawn_tree(SetupGame)

        for _ in range(4):
            player = self.game.players.next()
            self.spawn_tree(TakeTurn, player = player)