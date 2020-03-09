import collections

from renethack.util import validate

TileType = collections.namedtuple('TileType', 'name passable')
# name: str
# passable: bool

class World:
    """Represents the game world.

    Attributes:
        upper_levels: the list of levels above the current level.
        current_level: the current level. This level is updated every
            step. It also contains the hero.
        lower_levels: the list of levels below the current level.
        hero: the point on the current level that the hero is at.
    """

    def __init__(self, levels: list, hero: tuple) -> None:
        """Initialise a new `World` object.

        levels: the list of levels to use.
        hero: the point on the first level that the hero is at.
        """
        validate(self.__init__, locals())

        self.upper_levels = []
        self.current_level = levels[0]
        self.lower_levels = levels[1:]
        self.hero = hero

class Level:
    """Represents a game level."""

    def __init__(self, tiles: list, entities: list) -> None:
        """Initialises a new `Level` object.

        tiles: a 2D grid of tiles that describe the layout of the
            level.
        entities: the list of points that currently contain entities
            on the level.
        """
        validate(self.__init__, locals())

        self.tiles = tiles
        self.entities = entities

class Tile:
    """Represents a single tile."""

    def __init__(self, type: TileType, entity) -> None:
        """Initialise a new `Tile` object.

        `entity` can either be a `Monster` or a `Hero`.
        """
        validate(self.__init__, locals())

        self.type = type
        self.entity = entity

class ExistingEntityError(Exception):
    """
    Occurs when trying to add an entity to a tile that contains
    another entity.
    """

    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'entity already exists at {}'.format(self.point)

class TileNotPassableError(Exception):
    """Occurs when trying to add an entity to an unpassable tile."""

    def __init__(self, point: tuple) -> None:
        validate(self.__init__, locals())

        self.point = point

    def __str__(self) -> str:
        return 'tile at {} is unpassable'.format(self.point)
