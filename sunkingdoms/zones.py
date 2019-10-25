import random
import typing as t

from sunkingdoms.artifact import GameArtifact


class Zoneable(GameArtifact):
    pass


class ZoneOwner(object):
    pass


Z = t.TypeVar('Z', bound = Zoneable)


class Zone(t.Generic[Z]):

    def __init__(
        self,
        name: str,
        ordered: bool,
        private: bool,
        face_up: bool,
        owner: t.Optional[ZoneOwner] = None,
    ):
        self._name = name
        self._ordered = ordered
        self._private = private
        self._face_up = face_up
        self._owner = owner

        self._cardboards: t.List[Z] = []

    @property
    def name(self) -> str:
        return self._name

    def leave(self, cardboard: Z) -> None:
        self._cardboards.remove(cardboard)

    def join(self, cardboards: Z, index: t.Optional[int] = None) -> None:
        if cardboards.zone is not None:
            cardboards.zone.leave(cardboards)
        cardboards._zone = self
        if index is None:
            self._cardboards.append(cardboards)
        else:
            self._cardboards.insert(index, cardboards)

    def shuffle(self, to: t.Optional[int] = None) -> None:
        if to is None:
            random.shuffle(self._cardboards)
        else:
            self._cardboards[:to] = random.sample(
                self._cardboards[:to],
                to if to >= 0 else len(self._cardboards) + to
            )

    def __getitem__(self, item: int) -> Z:
        return self._cardboards.__getitem__(item)

    def __bool__(self) -> bool:
        return bool(self._cardboards)

    @property
    def cards(self) -> t.MutableSequence[Z]:
        return self._cardboards
