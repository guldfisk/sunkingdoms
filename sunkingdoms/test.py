from eventtree.replaceevent import EventSession
from gameframe.gamesession import GameSession
from sunkingdoms.interface import SKPlayerSignature, SKDummyController, SKDummyInterface
from sunkingdoms.livegame import LiveGame
from sunkingdoms.setup import SKSetup


def test():

    signatures = (SKPlayerSignature('player 1'),)

    setup_info = SKSetup(1)

    interface = SKDummyInterface(SKDummyController(signatures))

    game = LiveGame(setup_info, interface)

    game.start()

    # game_session = GameSession(
    #     observer_signatures = signatures,
    #     connection_controller_type = SKDummyController,
    #     interface_type = SKDummyInterface,
    #     setup_info = SKSetup(1),
    #     game_type = LiveGame,
    # )
    # game_session.start()
    # game_session.join()


# def other_test():
#     from gameframe.events import GameEvent, GameEventSUB
#
#     s = GameEventSUB(EventSession(), value = 10)
#     s.value = 21
#     print(s.value)


if __name__ == '__main__':
    test()