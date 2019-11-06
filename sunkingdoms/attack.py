from abc import abstractmethod, ABC

from gameframe.events import GameEvent


class Target(ABC):

    @abstractmethod
    def attack(self, damage: int, event: GameEvent):
        pass