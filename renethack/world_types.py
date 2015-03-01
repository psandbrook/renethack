import collections

from renethack.util import validate

TileType = collections.namedtuple('TileType', 'name passable')
# name: str
# passable: bool

class World:

    def __init__(self, levels: list, hero: tuple) -> None:
        validate(self.__init__, locals())

        self.upper_levels = []
        self.current_level = levels[0]
        self.lower_levels = levels[1:]
        self.hero = hero

class Level:

    def __init__(self, tiles: list, entities: list) -> None:
        validate(self.__init__, locals())

        self.tiles = tiles
        self.entities = entities

class Tile:

    def __init__(self, type: TileType, entity) -> None:
        validate(self.__init__, locals())

        self.type = type
        self.entity = entity

class ExistingEntityError(Exception):

    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'entity already exists at {}'.format(self.point)

class TileNotPassableError(Exception):

    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'tile at {} is unpassable'.format(self.point)
