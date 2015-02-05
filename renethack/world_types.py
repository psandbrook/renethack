import collections

from renethack.util import validate

TileType = collections.namedtuple('TileType', 'name passable')
# name: str
# passable: bool

class Level:

    # tiles: [[Tile]]
    # entities: [(int, int)]
    def __init__(self, tiles: list, entities: list) -> None:
        validate(self.__init__, locals())

        self.tiles = tiles
        self.entities = entities

class Tile:

    # type: TileType
    # items: [Item]
    # entity: Monster|Hero|None
    def __init__(self, type: TileType, items: list, entity) -> None:
        validate(self.__init__, locals())

        self.type = type
        self.items = items
        self.entity = entity

class ExistingEntityError(Exception):

    # point: (int, int)
    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'entity already exists at {}'.format(self.point)

class TileNotPassableError(Exception):

    # point: (int, int)
    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'tile at {} is unpassable'.format(self.point)
