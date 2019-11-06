from gameframe.signature import PlayerSignature


class SKPlayerSignature(PlayerSignature):

    def __init__(self, name: str):
        self._name = name

    @property
    def name(self) -> str:
        return self._name

    def __hash__(self) -> int:
        return hash(self._name)

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, self.__class__)
            and self._name == other._name
        )
