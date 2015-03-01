import random

import renethack
from renethack.world_types import World, Level, Tile, TileType, ExistingEntityError, TileNotPassableError
from renethack.entity_types import Hero
from renethack.util import validate, forany, rand_chance

MAX_MONSTERS = 6

SOLID_EARTH = TileType('Solid earth', passable=False)
WALL = TileType('Wall', passable=False)
FLOOR = TileType('Floor', passable=True)
UP_STAIRS = TileType('Upwards stairway', passable=True)
DOWN_STAIRS = TileType('Downwards stairway', passable=True)
CLOSED_DOOR = TileType('Closed door', passable=False)
OPEN_DOOR = TileType('Open door', passable=True)

def make_world(levels: int, level_length: int, hero: Hero) -> World:
    """Returns a randomly generated `World` object."""
    validate(make_world, locals())

    centre = (level_length - 1) // 2
    # The centre of each level.

    def make_level(up_stairs: bool, down_stairs: bool) -> Level:
        """Returns a randomly generated level as a `Level` object."""
        validate(make_level, locals())

        # Create a level initialised to solid earth:
        tiles = [
            [new_tile(SOLID_EARTH) for _ in range(level_length)]
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
            type_=WALL
            )

        fill_rect(
            level,
            point=(
                centre - centre_width//2,
                centre - centre_height//2
                ),
            width=centre_width,
            height=centre_height,
            type_=FLOOR
            )

        if up_stairs:
            level.tiles[centre][centre] = new_tile(UP_STAIRS)

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

                return forany(lambda t: t.type is FLOOR, tiles)

            walls = get_tiles(level, WALL)
            valid_walls = list(filter(valid_wall_point, walls))
            wall_point = random.choice(valid_walls)

            make_fn = random.choice(elements)

            if make_fn(level, wall_point):
                reject_count = 0
            else:
                reject_count += 1

        # Place the downwards stairway:
        if down_stairs:
            down_x, down_y = random.choice(get_tiles(level, FLOOR))
            level.tiles[down_x][down_y] = new_tile(DOWN_STAIRS)

        return level

    # Create a list of levels:
    world = ([make_level(False, True)]
        + [make_level(True, True) for _ in range(levels - 2)]
        + [make_level(True, False)])

    # Add the hero at the centre point on the first level:
    add_entity(world[0], (centre, centre), hero)

    return World(world, (centre, centre))

def new_tile(type_: TileType) -> Tile:
    """Returns a new `Tile` object that is initially empty."""
    validate(new_tile, locals())

    return Tile(
        type_,
        entity=None
        )

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

def check_fill_rect(
        level: Level,
        point: tuple,
        width: int,
        height: int,
        type_: TileType) -> None:
    """Fill a rectangular area on `level`.

    The area is only filled if every tile in the area has type
    `SOLID_EARTH`.

    Returns true if fill is successful, false otherwise.
    """
    validate(check_fill_rect, locals())

    x, y = point
    top_right = (x + width, y + height)
    level_length = len(level.tiles)

    if (not point_within(level_length, point)
            or not point_within(level_length, top_right)):
        return False

    for i in range(x, x + width):
        for j in range(y, y + height):

            if level.tiles[i][j].type != SOLID_EARTH:
                return False

    for i in range(x, x + width):
        for j in range(y, y + height):
            level.tiles[i][j] = new_tile(type_)

    return True

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
        type_=WALL
        )

    if north_check:

        fill_rect(
            level,
            point=(x - width//2, y + 1),
            width=width,
            height=height,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x - width//2 - 1, y),
            width=width + 2,
            height=1,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # South:

    south_check = check_fill_rect(
        level,
        point=(x - width//2 - 1, y - height - 1),
        width=width + 2,
        height=height + 1,
        type_=WALL
        )

    if south_check:

        fill_rect(
            level,
            point=(x - width//2, y - height),
            width=width,
            height=height,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x - width//2 - 1, y),
            width=width + 2,
            height=1,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # East:

    east_check = check_fill_rect(
        level,
        point=(x + 1, y - height//2 - 1),
        width=width + 1,
        height=height + 2,
        type_=WALL
        )

    if east_check:

        fill_rect(
            level,
            point=(x + 1, y - height//2),
            width=width,
            height=height,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x, y - height//2 - 1),
            width=1,
            height=height + 2,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # West:

    west_check = check_fill_rect(
        level,
        point=(x - width - 1, y - height//2 - 1),
        width=width + 1,
        height=height + 2,
        type_=WALL
        )

    if west_check:

        fill_rect(
            level,
            point=(x - width, y - height//2),
            width=width,
            height=height,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x, y - height//2 - 1),
            width=1,
            height=height + 2,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # If there is no space on any side:
    return False

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
        type_=WALL
        )

    if north_check:

        fill_rect(
            level,
            point=(x, y + 1),
            width=1,
            height=length,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x - 1, y),
            width=3,
            height=1,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # South:

    south_check = check_fill_rect(
        level,
        point=(x - 1, y - length - 1),
        width=3,
        height=length + 1,
        type_=WALL
        )

    if south_check:

        fill_rect(
            level,
            point=(x, y - length),
            width=1,
            height=length,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x - 1, y),
            width=3,
            height=1,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # East:

    east_check = check_fill_rect(
        level,
        point=(x + 1, y - 1),
        width=length + 1,
        height=3,
        type_=WALL
        )

    if east_check:

        fill_rect(
            level,
            point=(x + 1, y),
            width=length,
            height=1,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x, y - 1),
            width=1,
            height=3,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

        return True

    # West:

    west_check = check_fill_rect(
        level,
        point=(x - length - 1, y - 1),
        width=length + 1,
        height=3,
        type_=WALL
        )

    if west_check:

        fill_rect(
            level,
            point=(x - length, y),
            width=length,
            height=1,
            type_=FLOOR
            )

        fill_rect(
            level,
            point=(x, y - 1),
            width=1,
            height=3,
            type_=WALL
            )

        level.tiles[x][y] = new_tile(CLOSED_DOOR)

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

def remove_entity(level: Level, point: tuple) -> None:
    """Removes the entity on `level` at `point`."""
    validate(remove_entity, locals())

    x, y = point
    level.tiles[x][y].entity = None
    level.entities = [None if p == point else p for p in level.entities]

def step(world: World):
    """Update `world` by one step.

    The contents of `world` may by modified.
    """
    validate(step, locals())

    level_length = len(world.current_level.tiles)

    # Randomly place a new monster:
    if len(world.current_level.entities) - 1 < MAX_MONSTERS:

        x = random.randrange(level_length)
        y = random.randrange(level_length)
        tile = world.current_level.tiles[x][y]

        if (tile.entity is None
                and tile.type is FLOOR
                and rand_chance(0.1)):

            monster_fn = random.choice(renethack.entity.monster_fns)
            add_entity(world.current_level, (x, y), monster_fn())

    # Update each entity on the current level:
    for entity_point in world.current_level.entities:

        # Skip over removed entities:
        if entity_point is None:
            continue

        x, y = entity_point
        entity = world.current_level.tiles[x][y].entity
        old_world_len = len(world.upper_levels)

        entity.step(entity_point, world)

        if old_world_len != len(world.upper_levels):
            # Return immediately if the world has changed.
            return

    # Clean up removed entities:
    world.current_level.entities = [
        p for p in world.current_level.entities
        if p is not None
        ]

elements = [make_room, make_corridor]
# The list of functions that add an element to a level.
