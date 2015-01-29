import collections
import random

from renethack.entity import Hero, Monster
from renethack.util import validate, forany

MAX_MONSTERS = 10

Level = collections.namedtuple('Level', 'tiles entities')
# tiles: [[Tile]]
# entities: [(int, int)]

Tile = collections.namedtuple('Tile', 'type items entity')
# type: TileType
# items: [Item]
# entity: Monster|Hero|None

TileType = collections.namedtuple('TileType', 'name passable')
# name: str
# passable: bool

solid_earth = TileType('solid_earth', passable=False)
wall = TileType('wall', passable=False)
floor = TileType('floor', passable=True)
up_stairs = TileType('up_stairs', passable=True)
down_stairs = TileType('down_stairs', passable=True)
closed_door = TileType('closed_door', passable=False)
open_door = TileType('open_door', passable=True)

# point: (int, int)
def apply_point(level: Level, point: tuple) -> Tile:
    """Return the `Tile` given by applying `point` to `level`."""
    validate(apply_point, locals())

    x, y = point
    return level.tiles[x][y]

# return: ([Level], Level, [Level])
def make_world(levels: int, level_length: int, hero: Hero) -> tuple:
    """Returns a randomly generated dungeon.

    return: ([Level], Level, [Level])
        first: levels above the current one
        second: current level
        third: levels below the current one
    """
    validate(make_world, locals())

    centre = int((level_length-1) / 2)
    # The centre of each level.

    def make_level(place_down_stairs: bool) -> Level:
        """Returns a randomly generated level as a `Level` object."""
        validate(make_level, locals())

        # Create a level initialised to solid earth:
        tiles = [
            [new_tile(solid_earth) for _ in range(level_length)]
            for _ in range(level_length)
            ]

        level = Level(tiles=tiles, entities=[])

        # Create the centre room:
        centre_width = rand_room_len()
        centre_height = rand_room_len()

        # From the centre point, go west by centre_width / 2
        # and south by centre_height / 2.
        centre_fill_point = south(
            int(centre_height/2),
            west(int(centre_width/2), (centre, centre))
            )

        fill_rect(
            level=level,
            point=centre_fill_point,
            width=centre_width+2,
            height=centre_height+2,
            type=wall
            )

        fill_rect(
            level=level,
            point=northeast(1, centre_fill_point),
            width=centre_width,
            height=centre_height,
            type=floor
            )

        level[centre][centre] = new_tile(up_stairs)

        # Keep creating rooms until there are
        # 1000 contiguous rejections:
        reject_count = 0
        while reject_count < 1000:

            # point: (int, int)
            def valid_wall_point(point: tuple) -> bool:
                """Check if `point` is a valid wall point.

                A point is a valid wall point if any point in the
                four cardinal directions surrounding the given point
                leads to a floor tile.
                """
                validate(valid_wall_point, locals())

                points = [
                    north(1, point),
                    south(1, point),
                    east(1, point),
                    west(1, point)
                    ]

                tiles = [apply_point(level, p) for p in points]

                return forany(lambda t: t.type is floor, tiles)

            walls = get_tiles(level, wall)
            valid_walls = list(filter(valid_wall_point, walls))
            wall_point = random.choice(valid_walls)

            make_fn = random.choice(elements)

            if make_fn(level, wall_point):
                reject_count = 0
            else:
                reject_count += 1

        # Place the downwards stairway:
        if place_down_stairs:
            down_x, down_y = random.choice(get_tiles(level, floor))
            level[down_x][down_y] = new_tile(down_stairs)

        return Level(tiles=level, entities=[])

    # Create a list of levels:
    world = [make_level(True) for _ in range(levels-1)] + [make_level(False)]

    # Add the hero at the centre point on the first level:
    add_entity(world[0], (centre, centre), hero)

    return ([], world[0], world[1:])

# TileType -> Tile
def new_tile(type):
    """Returns a new `Tile` object that is initially empty."""
    return Tile(
        type=type,
        flashing=False,
        items=[],
        entity=None
        )

# ([[Tile]], (int, int), int, int, TileType) -> None
def fill_rect(level, point, width, height, type):
    """Fill a rectangular area on `level`."""

    x, y = point

    for i in range(x, x + width):
        for j in range(y, y + height):
            level[i][j] = new_tile(type)

# ([[Tile]], (int, int), int, int, TileType) -> None
def check_fill_rect(level, point, width, height, type):
    """Fill a rectangular area on `level`.

    The area is only filled if every tile in the area has type
    `solid_earth`.

    Returns true if fill is successful, false otherwise.
    """

    x, y = point

    for i in range(x, x + width):
        for j in range(y, y + height):

            if level[i][j].type != solid_earth:
                return False

    for i in range(x, x + width):
        for j in range(y, y + height):
            level[i][j] = new_tile(type)

    return True

# ([[Tile]], (int, int)) -> bool
def make_room(level, wall_point):
    """Create a room on `level` at `wall_point`.

    The tile at `wall_point` should be a wall.
    """

    width = rand_room_len()
    height = rand_room_len()

    # North:
    north_fill_point = north(1, west(int(width/2), wall_point))
    if check_fill_rect(level, north_fill_point, width+2, height+1, wall):

        fill_rect(level, east(1, north_fill_point), width, hight, floor)
        fill_rect(level, south(1, north_fill_point), width+2, 1, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # South:
    south_fill_point = west(int(width/2), south(height+1, wall_point))
    if check_fill_rect(level, south_fill_point, width+2, height+1, wall):

        fill_rect(level, northeast(1, south_fill_point), width, height, floor)
        fill_rect(level, north(height+1, south_fill_point), width+2, 1, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # East:
    east_fill_point = east(1, south(int(height/2), wall_point))
    if check_fill_rect(level, east_fill_point, width+1, height+2, wall):

        fill_rect(level, north(1, east_fill_point), width, height, floor)
        fill_rect(level, west(1, east_fill_point), 1, height+2, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # West:
    west_fill_point = west(width+1, south(int(height/2), wall_point))
    if check_fill_rect(level, west_fill_point, width+1, height+2, wall):

        fill_rect(level, northeast(1, west_fill_point), width, height, floor)
        fill_rect(level, east(width+1, west_fill_point), 1, height+2, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # If there is no space on any side:
    return False

# ([[Tile]], (int, int)) -> bool
def make_corridor(level, wall_point):
    """Create a corridor on `level` at `wall_point`.

    The tile at `wall_point` should be a wall.
    """

    length = random.randint(5, 15)

    # North:
    if check_fill_rect(level, northwest(1, wall_point), 3, length+1, wall):

        fill_rect(level, north(1, wall_point), 1, length, floor)
        fill_rect(level, west(1, wall_point), 3, 1, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # South:
    south_fill_point = west(1, south(length+1, wall_point))
    if check_fill_rect(level, south_fill_point, 3, length+1, wall):

        fill_rect(level, northeast(1, south_fill_point), 1, length, floor)
        fill_rect(level, west(1, wall_point), 3, 1, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # East:
    if check_fill_rect(level, northeast(1, wall_point), length+1, 3, wall):

        fill_rect(level, east(1, wall_point), length, 1, floor)
        fill_rect(level, south(1, wall_point), 1, 3, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # West:
    west_fill_point = south(1, west(length+1, wall_point))
    if check_fill_rect(level, west_fill_point, length+1, 3, wall):

        fill_rect(level, northeast(1, west_fill_point), length, 1, floor)
        fill_rect(level, south(1, wall_point), 1, 3, wall)

        x, y = wall_point
        level[x][y] = new_tile(closed_door)

        return True

    # If there is no space on any side:
    return False

elements = [make_room, make_corridor]
# The list of functions that add an element to a level.

# ([[Tile]], TileType) -> [(int, int)]
def get_tiles(level, type):
    """Returns the list of points on `level` with tile type `type`."""
    level_length = len(level)
    return [
        (x, y)
        for x in range(level_length)
        for y in range(level_length)
        if level[x][y].type == type
        ]

# () -> int
def rand_room_len():
    """Returns a random integer suitable for the length of a room."""
    return random.randint(4, 7)

# (int, (int, int)) -> (int, int)
def north(amount, point):
    x, y = point
    return (x, y + amount)

# (int, (int, int)) -> (int, int)
def south(amount, point):
    x, y = point
    return (x, y - amount)

# (int, (int, int)) -> (int, int)
def east(amount, point):
    x, y = point
    return (x + amount, y)

# (int, (int, int)) -> (int, int)
def west(amount, point):
    x, y = point
    return (x - amount, y)

# (int, (int, int)) -> (int, int)
def northeast(amount, point):
    x, y = point
    return (x + amount, y + amount)

# (int, (int, int)) -> (int, int)
def southeast(amount, point):
    x, y = point
    return (x + amount, y - amount)

# (int, (int, int)) -> (int, int)
def southwest(amount, point):
    x, y = point
    return (x - amount, y - amount)

# (int, (int, int)) -> (int, int)
def northwest(amount, point):
    x, y = point
    return (x - amount, y + amount)

# (Level, (int, int), Monster|Hero) -> None
def add_entity(level, point, entity):
    x, y = point
    level.tiles[x][y].entity = entity
    level.entities.append(point)

# (Level, (int, int)) -> None
def remove_entity(level, point):
    x, y = point
    level.tiles[x][y].entity = None
    level.entities = [None if p == point else p for p in level.entities]

# (([Level], Level, [Level]), ([Level], Level, [Level])) -> bool
def worlds_eq(world1, world2):  
    return len(world1[0]) == len(world2[0])

# ([Level], Level, [Level]) -> ([Level], Level, [Level])
def step(world):

    _, current_level, _ = world
    level_length = len(current_level.tiles)

    # Randomly place new monsters:
    if len(current_level.entities) < MAX_MONSTERS:

        for x in range(level_length):
            for y in range(level_length):


    # Update each entity on the current level:
    for entity_point in current_level.entities:

        # Skip over removed entities:
        if entity_point is None:
            continue

        x, y = entity_point
        entity = current_level.tiles[x][y].entity

        if type(entity) is Hero:
            new_world = entity.step(entity_point, world)

            if not worlds_eq(new_world, world):
                # Return immediately if the world has changed.
                return new_world

        else:
            entity.step(entity_point, world)

    # Clean up removed entities:
    current_level.entities = [
        p for p in current_level.entities
        if p is not None
        ]

    return world
