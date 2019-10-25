from gameframe.setupinfo import SetupInfo


class SKSetup(SetupInfo):

    def __init__(self, player_count: int):
        self._player_count = player_count

    @property
    def player_count(self) -> int:
        return self._player_count