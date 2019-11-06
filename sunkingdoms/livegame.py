from sunkingdoms import events
from sunkingdoms.game.game import SKGame


class LiveGame(SKGame):

    def start(self):
        self.resolve_event(events.PlayGame)
