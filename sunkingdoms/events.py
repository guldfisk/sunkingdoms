import typing as t

from abc import abstractmethod

from eventtree.replaceevent import EventCheckException, EventResolutionException
from gameframe.events import GameEvent
from gameframe.interface import Option
from sunkingdoms.artifacts.artifacts import Card, Cardboard, CardType, Action
from sunkingdoms import cards
from sunkingdoms.attack import Target
from sunkingdoms.game.interface import SKGame
from sunkingdoms.players.interface import SKPlayer
from sunkingdoms.setup import SKSetup
from sunkingdoms.zones import Zone


class SKGameEvent(GameEvent):
    player: SKPlayer

    @property
    def game(self) -> SKGame:
        return self._session

    @abstractmethod
    def payload(self, **kwargs):
        pass

    def serialize(self) -> t.Any:
        pass

    def deserialize(self, s: t.Any) -> GameEvent:
        pass


class CreateCardboard(SKGameEvent):
    to: Zone
    card_type: t.Type[Card]
    face_up: bool

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
    target: Cardboard
    frm: Zone
    to: Zone
    index: int

    def setup(self, **kwargs):
        self._values.setdefault('index', None)

    def check(self, **kwargs):
        if not self.target in self.frm:
            raise EventCheckException()

    def payload(self, **kwargs):
        self.to.join(self.target)
        if self.frm.name == 'battlefield':
            self.target.card.actions.refresh()
        return self.target
    
    
class Reshuffle(SKGameEvent):

    def payload(self, **kwargs):
        if self.player.library:
            index = len(self.player.discard_pile)
            for cardboard in self.player.discard_pile:
                self.spawn_tree(
                    MoveCardboard,
                    frm=self.player.discard_pile,
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
    amount: int

    def payload(self, **kwargs):
        cardboards = []
        for _ in range(self.amount):
            cardboard = self.spawn_tree(DrawCardboard)
            if cardboard is None:
                break
            cardboards.append(cardboard)
        return cardboards
    
    
class DrawHand(SKGameEvent):
    amount: int

    def setup(self, **kwargs):
        self._values.setdefault('amount', 5)

    def payload(self, **kwargs):
        return self.depend_tree(DrawCardboards)


class RefillTradeRow(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('to', self.game.trade_row)
        self._values.setdefault('frm', self.game.trade_deck)
        self._values.setdefault('target', self.game.trade_deck[-1] if self.game.trade_deck else None)

    def payload(self, **kwargs):
        return self.depend_tree(MoveCardboard)


class ShuffleZone(SKGameEvent):
    to: Zone

    def payload(self, **kwargs):
        self.to.shuffle()


class SetupGame(SKGameEvent):
    setup_info: SKSetup

    def payload(self, **kwargs):
        for _ in range(10):
            self.spawn_tree(
                CreateCardboard,
                card_type = cards.FederationShuttle,
                to = self.game.trade_deck,
            )
        for _ in range(10):
            self.spawn_tree(
                CreateCardboard,
                card_type = cards.Cutter,
                to = self.game.trade_deck,
            )

        self.spawn_tree(ShuffleZone, to = self.game.trade_deck)

        for _ in range(5):
            self.spawn_tree(RefillTradeRow)

        for player in self.game.players.all:
            for _ in range(5):
                self.spawn_tree(
                    CreateCardboard,
                    card_type = cards.MechWorld,
                    to = player.discard_pile,
                )
            for _ in range(5):
                self.spawn_tree(
                    CreateCardboard,
                    card_type = cards.BlobFighter,
                    to = player.discard_pile,
                )

        for player in self.game.players.all:
            self.spawn_tree(DrawHand, player = player)


class Move(Option):

    def __init__(self, option_type: str, value: str, callback: t.Callable[[], None]):
        super().__init__(option_type, value)
        self._callback = callback

    def do(self) -> None:
        self._callback()


class CastCardboard(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('frm', self.player.hand)
        self._values.setdefault('to', self.player.battlefield)

    def payload(self, **kwargs):
        self.depend_tree(MoveCardboard)
        self.target.card.on_play(self)


class DestroyCardboard(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('frm', self.player.battlefield)
        self._values.setdefault('to', self.player.discard_pile)

    def payload(self, **kwargs):
        self.depend_tree(MoveCardboard)


class DiscardCardboard(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('frm', self.player.hand)
        self._values.setdefault('to', self.player.discard_pile)

    def payload(self, **kwargs):
        self.spawn_tree(MoveCardboard)


class ScrapCardboard(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('to', self.game.scrap_pile)

    def payload(self, **kwargs):
        self.spawn_tree(MoveCardboard)


class Attack(SKGameEvent):
    target: Target
    amount: int

    def payload(self, **kwargs):
        self.depend_tree(SubtractDamage)
        self.target.attack(self.amount, self)


class AddMoney(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.money += self.amount


class SubtractMoney(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.money -= self.amount


class PayMoney(SKGameEvent):
    amount: int

    def check(self, **kwargs):
        if not self.player.money >= self.amount:
            raise EventCheckException()

    def payload(self, **kwargs):
        self.depend_tree(SubtractMoney)


class BuyCardboard(SKGameEvent):
    target: Cardboard
    frm: Zone
    to: Zone

    def setup(self, **kwargs):
        self._values.setdefault('frm', self.game.trade_row)
        self._values.setdefault('to', self.player.discard_pile)

    def payload(self, **kwargs):
        self.depend_tree(PayMoney, amount = self.target.card.price.amount)
        self.spawn_tree(MoveCardboard)
        self.branch(RefillTradeRow, player = self.player)


class AddDamage(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.damage += self.amount


class SubtractDamage(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.damage -= self.amount


class ResetResources(SKGameEvent):

    def payload(self, **kwargs):
        self.player.money = 0
        self.player.damage = 0


class ActivateAction(SKGameEvent):
    target: Cardboard
    action: Action

    def payload(self, **kwargs):
        self.action.cost(self)
        self.action.do(self)
        self.action.exhaust()


class GainInfluence(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.influence += self.amount


class LoseInfluence(SKGameEvent):
    amount: int

    def payload(self, **kwargs):
        self.player.influence -= self.amount


class TakeTurn(SKGameEvent):

    def _play_cardboard_action(self, cardboard: Cardboard) -> Move:
        return Move(
            'play card',
            cardboard.card.name,
            lambda : self.spawn_tree(
                CastCardboard,
                target = cardboard,
            )
        )

    def _buy_cardboard_action(self, cardboard: Cardboard) -> Move:
        return Move(
            'buy card',
            cardboard.card.name,
            lambda : self.spawn_tree(
                BuyCardboard,
                target = cardboard,
            )
        )

    def _activate_cardboard_action(self, cardboard: Cardboard, action: Action):
        return Move(
            'activate cardboard',
            cardboard.card.name,
            lambda : self.spawn_tree(
                ActivateAction,
                target = cardboard,
                action = action,
            )
        )

    def _attack_action(self, target: Target):
        return Move(
            'attack',
            target.card.name if isinstance(target, Cardboard) else target.signature.name,
            lambda : self.spawn_tree(
                Attack,
                target = target,
                amount = target.card.health if isinstance(target, Cardboard) else self.player.damage,
            )
        )

    def payload(self, **kwargs):
        while True:
            moves: t.List[Move] = []
            for cardboard in self.player.hand:
                moves.append(self._play_cardboard_action(cardboard))

            for cardboard in self.game.trade_row:
                if cardboard.card.price.amount <= self.player.money:
                    moves.append(
                        self._buy_cardboard_action(cardboard)
                    )

            for cardboard in self.player.battlefield:
                for action in cardboard.card.actions:
                    if action.available(self):
                        moves.append(
                            self._activate_cardboard_action(
                                cardboard,
                                action,
                            )
                        )

            if self.player.damage:
                for target in self.player.opponent.get_legal_targets(self.player.damage):
                    moves.append(
                        self._attack_action(
                            target
                        )
                    )

            if not moves:
                break

            pass_turn = Move('pass turn', 'pass turn', lambda : None)

            moves.append(pass_turn)

            move = self.game.interface.select_option(
                self.player,
                moves,
            )

            if move == pass_turn:
                break

            move.do()

        for cardboard in self.player.battlefield.iter_copy():
            if not cardboard.card.card_type == CardType.BASE:
                self.spawn_tree(DestroyCardboard, target = cardboard)
            else:
                cardboard.card.actions.refresh()

        for cardboard in self.player.hand.iter_copy():
            self.spawn_tree(DiscardCardboard, target = cardboard)

        self.spawn_tree(ResetResources)
        self.spawn_tree(DrawHand)


class GameFinished(SKGameEvent):
    winner: SKPlayer

    def payload(self, **kwargs):
        pass


class PlayGame(SKGameEvent):
    setup_info: SKSetup

    def _check_game_end(self) -> t.Optional[SKPlayer]:
        for player in self.game.players.all:
            if player.influence <= 0:
                return self.game.players.loop_from(player).__next__()

    def payload(self, **kwargs):
        self.spawn_tree(SetupGame)

        while True:
            player = self.game.players.next()
            self.spawn_tree(TakeTurn, player = player)
            winner = self._check_game_end()
            if winner:
                self.spawn_tree(GameFinished, winner = winner)
                break