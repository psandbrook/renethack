import random

import renethack
from renethack.world_types import Level, Tile, TileType, ExistingEntityError, TileNotPassableError
from renethack.entity_types import Hero
from renethack.util import validate, forany, rand_chance

MAX_MONSTERS = 6

solid_earth = TileType('Solid earth', passable=False)
wall = TileType('Wall', passable=False)
floor = TileType('Floor', passable=True)
up_stairs = TileType('Upwards stairway', passable=True)
down_stairs = TileType('Downwards stairway', passable=True)
closed_door = TileType('Closed door', passable=False)
open_door = TileType('Open door', passable=True)

# return: ([Level], Level, [Level])
def make_world(levels: int, level_length: int, hero: Hero) -> tuple:
    """Returns a randomly generated dungeon.

    return: ([Level], Level, [Level])
        levels above the current one
        second: current level
        third: levels below the current one
    """
    validate(make_world, locals())

    centre = (level_length - 1) // 2
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

        fill_rect(
            level,
            point=(
                centre - centre_width//2 - 1,
                centre - centre_height//2 - 1
                ),
            width=centre_width + 2,
            height=centre_height + 2,
            type_=wall
            )

        fill_rect(
            level,
            point=(
                centre - centre_width//2,
                centre - centre_height//2
                ),
            width=centre_width,
            height=centre_height,
            type_=floor
            )

        level.tiles[centre][centre] = new_tile(up_stairs)

        # Keep creating rooms until there are
        # 20 contiguous rejections:
        reject_count = 0
        while reject_count < 20:

            # point: (int, int)
            def valid_wall_point(point: tuple) -> bool:
                """Check if `point` is a valid wall point.

                A point is a valid wall point if any point in the
                four cardinal directions surrounding the given point
                leads to a floor tile.
                """
                validate(valid_wall_point, locals())

                x, y = point

                points = [
                    (x, y + 1),
                    (x, y - 1),
                    (x + 1, y),
                    (x - 1, y)
                    ]

                for p in points:
                    if not point_within(level_length, p):
                        return False

                tiles = [level.tiles[x][y] for x, y in points]

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
            level.tiles[down_x][down_y] = new_tile(down_stairs)

        return level

    # Create a list of levels:
    world = ([make_level(place_down_stairs=True) for _ in range(levels - 1)]
        + [make_level(place_down_stairs=False)])

    # Add the hero at the centre point on the first level:
    add_entity(world[0], (centre, centre), hero)

    return ([], world[0], world[1:])

# TileType -> Tile
def new_tile(type_: TileType) -> Tile:
    """Returns a new `Tile` object that is initially empty."""
    validate(new_tile, locals())

    return Tile(
        type_,
        items=[],
        entity=None
        )

# point: (int, int)
def fill_rect(
        level: Level,
        point: tuple,
        width: int,
        height: int,
        type_: TileType) -> None:
    """Fill a rectangular area on `level`."""
    validate(fill_rect, locals())

    x, y = point

    for i in range(x, x + width):
        for j in range(y, y + height):
            level.tiles[i][j] = new_tile(type_)

# point: (int, int)
def check_fill_rect(
        level: Level,
        point: tuple,
        width: int,
        height: int,
        type_: TileType) -> None:
    """Fill a rectangular area on `level`.

    The area is only filled if every tile in the area has type
    `solid_earth`.

    Returns true if fill is successful, false otherwise.
    """
    validate(check_fill_rect, locals())

    x, y = point
    level_length = len(level.tiles)

    if (not point_within(level_length, point)
            or not point_within(level_length, (x + width, y + height))):
        return False

    for i in range(x, x + width):
        for j in range(y, y + height):

            if level.tiles[i][j].type != solid_earth:
                return False

    for i in range(x, x + width):
        for j in range(y, y + height):
            level.tiles[i][j] = new_tile(type_)

    return True

# wall_point: (int, int)
def make_room(level: Level, wall_point: tuple) -> bool:
    """Create a room on `level` at `wall_point`.

    The tile at `wall_point` should be a wall.
    """
    validate(make_room, locals())

    x, y = wall_point
    width = rand_room_len()
    height = rand_room_len()

    # North:

    north_check = check_fill_rect(
        level,
        point=(x - width//2 - 1, y + 1),
        width=width + 2,
        height=height + 1,
        type_=wall
        )

    if north_check:

        fill_rect(
            level,
            point=(x - width//2, y + 1),
            width=width,
            height=height,
            type_=floor
            )

        fill_rect(
            level,
            point=(x - width//2 - 1, y),
            width=width + 2,
            height=1,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # South:

    south_check = check_fill_rect(
        level,
        point=(x - width//2 - 1, y - height - 1),
        width=width + 2,
        height=height + 1,
        type_=wall
        )

    if south_check:

        fill_rect(
            level,
            point=(x - width//2, y - height),
            width=width,
            height=height,
            type_=floor
            )

        fill_rect(
            level,
            point=(x - width//2 - 1, y),
            width=width + 2,
            height=1,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # East:

    east_check = check_fill_rect(
        level,
        point=(x + 1, y - height//2 - 1),
        width=width + 1,
        height=height + 2,
        type_=wall
        )

    if east_check:

        fill_rect(
            level,
            point=(x + 1, y - height//2),
            width=width,
            height=height,
            type_=floor
            )

        fill_rect(
            level,
            point=(x, y - height//2 - 1),
            width=1,
            height=height + 2,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # West:

    west_check = check_fill_rect(
        level,
        point=(x - width - 1, y - height//2 - 1),
        width=width + 1,
        height=height + 2,
        type_=wall
        )

    if west_check:

        fill_rect(
            level,
            point=(x - width, y - height//2),
            width=width,
            height=height,
            type_=floor
            )

        fill_rect(
            level,
            point=(x, y - height//2 - 1),
            width=1,
            height=height + 2,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # If there is no space on any side:
    return False

# wall_point: (int, int)
def make_corridor(level: Level, wall_point: tuple) -> bool:
    """Create a corridor on `level` at `wall_point`.

    The tile at `wall_point` should be a wall.
    """
    validate(make_corridor, locals())

    x, y = wall_point
    length = random.randint(5, 15)

    # North:

    north_check = check_fill_rect(
        level,
        point=(x - 1, y + 1),
        width=3,
        height=length + 1,
        type_=wall
        )

    if north_check:

        fill_rect(
            level,
            point=(x, y + 1),
            width=1,
            height=length,
            type_=floor
            )

        fill_rect(
            level,
            point=(x - 1, y),
            width=3,
            height=1,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # South:

    south_check = check_fill_rect(
        level,
        point=(x - 1, y - length - 1),
        width=3,
        height=length + 1,
        type_=wall
        )

    if south_check:

        fill_rect(
            level,
            point=(x, y - length),
            width=1,
            height=length,
            type_=floor
            )

        fill_rect(
            level,
            point=(x - 1, y),
            width=3,
            height=1,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # East:

    east_check = check_fill_rect(
        level,
        point=(x + 1, y - 1),
        width=length + 1,
        height=3,
        type_=wall
        )

    if east_check:

        fill_rect(
            level,
            point=(x + 1, y),
            width=length,
            height=1,
            type_=floor
            )

        fill_rect(
            level,
            point=(x, y - 1),
            width=1,
            height=3,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # West:

    west_check = check_fill_rect(
        level,
        point=(x - length - 1, y - 1),
        width=length + 1,
        height=3,
        type_=wall
        )

    if west_check:

        fill_rect(
            level,
            point=(x - length, y),
            width=length,
            height=1,
            type_=floor
            )

        fill_rect(
            level,
            point=(x, y - 1),
            width=1,
            height=3,
            type_=wall
            )

        level.tiles[x][y] = new_tile(closed_door)

        return True

    # If there is no space on any side:
    return False

def get_tiles(level: Level, type_: TileType) -> list:
    """Returns the list of points on `level` with tile type `type_`."""
    validate(get_tiles, locals())

    level_length = len(level.tiles)

    return [
        (x, y)
        for x in range(level_length)
        for y in range(level_length)
        if level.tiles[x][y].type is type_
        ]

def rand_room_len() -> int:
    """Returns a random integer suitable for the length of a room."""
    return random.randint(4, 7)

def point_within(length: int, point: tuple) -> bool:
    """
    Check whether a point is within a square grid
    of length `length`.
    """
    validate(point_within, locals())

    x, y = point
    return 0 <= x < length and 0 <= y < length

# point: (int, int)
def add_entity(level: Level, point: tuple, entity) -> None:
    """Adds an entity to `level` at `point`."""
    validate(add_entity, locals())

    x, y = point
    tile = level.tiles[x][y]

    if tile.entity is not None:
        raise ExistingEntityError(point)

    elif not tile.type.passable:
        raise TileNotPassableError(point)

    else:
        tile.entity = entity
        level.entities.append(point)

# point: (int, int)
def remove_entity(level: Level, point: tuple) -> None:
    """Removes the entity on `level` at `point`."""
    validate(remove_entity, locals())

    x, y = point
    level.tiles[x][y].entity = None
    level.entities = [None if p == point else p for p in level.entities]

# world1: ([Level], Level, [Level])
# world2: ([Level], Level, [Level])
def worlds_eq(world1: tuple, world2: tuple) -> bool:
    """Checks if two worlds are equal."""
    validate(worlds_eq, locals())

    return len(world1[0]) == len(world2[0])

# world: ([Level], Level, [Level])
# return: ([Level], Level, [Level])
def step(world: tuple) -> tuple:
    """Update `world` by one step.

    The contents of `world` may by modified.
    May return a different `world` value.
    """
    validate(step, locals())

    _, current_level, _ = world
    level_length = len(current_level.tiles)

    # Randomly place a new monster:
    if len(current_level.entities) - 1 < MAX_MONSTERS:

        x = random.randrange(level_length)
        y = random.randrange(level_length)
        tile = current_level.tiles[x][y]

        if (tile.entity is None
                and tile.type is floor
                and rand_chance(0.1)):

            monster_fn = random.choice(renethack.entity.monster_fns)
            add_entity(current_level, (x, y), monster_fn())

    # Update each entity on the current level:
    for entity_point in current_level.entities:

        # Skip over removed entities:
        if entity_point is None:
            continue

        x, y = entity_point
        entity = current_level.tiles[x][y].entity

        if isinstance(entity, Hero):
            new_world = entity.step(entity_point, world)

            if not worlds_eq(new_world, world):
                # Return immediately if the world has changed.
                return new_world

        else:
            entity.step(entity_point, current_level)

    # Clean up removed entities:
    current_level.entities = [
        p for p in current_level.entities
        if p is not None
        ]

    return world

elements = [make_room, make_corridor]
# The list of functions that add an element to a level.
