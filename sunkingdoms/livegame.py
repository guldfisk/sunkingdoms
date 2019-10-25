from sunkingdoms import events
from sunkingdoms.game import SKGame


class LiveGame(SKGame):

    def start(self):
        print('game startet')
        self.resolve_event(events.PlayGame)
        print('game ended')