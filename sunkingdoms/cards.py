from gameframe.events import GameEvent
from sunkingdoms.artifacts import Card, Price, Cardboard


class Scout(Card):
    name = 'Scout'
    price = Price(0)

    def on_play(self, cardboard: Cardboard, event: GameEvent):
        print('played scout')


class Viper(Card):
    name = 'viper'
    price = Price(0)

    def on_play(self, cardboard: Cardboard, event: GameEvent):
        print('played viper')


class FederationShuttle(Card):
    name = 'Federation Shuttle'
    price = Price(1)

    def on_play(self, cardboard: Cardboard, event: GameEvent):
        print('played Federation Shuttle')