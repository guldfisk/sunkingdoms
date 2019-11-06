import random
import typing as t
import copy

from sunkingdoms.artifacts.artifact import GameArtifact


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

    @property
    def owner(self) -> t.Optional[ZoneOwner]:
        return self._owner

    def leave(self, cardboard: Z) -> None:
        self._cardboards.remove(cardboard)

    def join(self, cardboard: Z, index: t.Optional[int] = None) -> None:
        if cardboard.zone is not None:
            cardboard.zone.leave(cardboard)
        cardboard._zone = self
        if index is None:
            self._cardboards.append(cardboard)
        else:
            self._cardboards.insert(index, cardboard)

    def shuffle(self, to: t.Optional[int] = None) -> None:
        if to is None:
            random.shuffle(self._cardboards)
        else:
            self._cardboards[:to] = random.sample(
                self._cardboards[:to],
                to if to >= 0 else len(self._cardboards) + to
            )

    def iter_copy(self) -> t.Iterator[Z]:
        return copy.copy(self._cardboards).__iter__()

    def __getitem__(self, item: int) -> Z:
        return self._cardboards.__getitem__(item)

    def __iter__(self) -> t.Iterator[Z]:
        return self._cardboards.__iter__()

    def __bool__(self) -> bool:
        return bool(self._cardboards)

    def __len__(self) -> int:
        return len(self._cardboards)

    def __contains__(self, item: Z) -> bool:
        return self._cardboards.__contains__(item)

    def __repr__(self) -> str:
        return '{}({})'.format(
            self.__class__.__name__,
            self._name,
        )

    @property
    def cards(self) -> t.MutableSequence[Z]:
        return self._cardboards
