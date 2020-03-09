import random

import renethack
from renethack.world_types import World, Level, Tile, TileType, ExistingEntityError, TileNotPassableError
from renethack.entity_types import Hero
from renethack.util import validate, forany, rand_chance

MAX_MONSTERS = 6
# The maximum number of monsters allowed per level.

SOLID_EARTH = TileType('Solid earth', passable=False)
WALL = TileType('Wall', passable=False)
FLOOR = TileType('Floor', passable=True)
UP_STAIRS = TileType('Upwards stairway', passable=True)
DOWN_STAIRS = TileType('Downwards stairway', passable=True)
CLOSED_DOOR = TileType('Closed door', passable=False)
OPEN_DOOR = TileType('Open door', passable=True)

def make_world(levels: int, level_length: int, hero: Hero) -> World:
    """
    Returns a new `World` object, with each level randomly generated.

    levels: the number of levels generated.
    level_length: the length of the side of each level.
    hero: the `Hero` object to place on the first level.
    """
    validate(make_world, locals())

    centre = (level_length - 1) // 2
    # (centre, centre) denotes the centre of each level.

    def make_level(up_stairs: bool, down_stairs: bool) -> Level:
        """Returns a randomly generated `Level` object.

        up_stairs: whether to place an upwards stairway on the level.
        down_stairs: whether to place a downwards stairway on the
            level.
        """
        validate(make_level, locals())

        # The level must first be initialised to contain only
        # `SOLID_EARTH` tiles.

        tiles = [
            [new_tile(SOLID_EARTH) for _ in range(level_length)]
            for _ in range(level_length)
            ]

        level = Level(tiles=tiles, entities=[])

        # The centre room must be created manually so it can be used
        # as a starting point for generating the other rooms.

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

        # An upwards stairway should not be placed on the first level.
        if up_stairs:
            level.tiles[centre][centre] = new_tile(UP_STAIRS)

        # Try to keep placing rooms until there have been 20
        # continuous rejections.

        reject_count = 0
        while reject_count < 20:

            def valid_wall_point(point: tuple) -> bool:
                """Check if `point` is a valid wall point.

                A point is a valid wall point if any adjacent
                (north, south, east, west) point is a floor tile.
                """
                validate(valid_wall_point, locals())

                x, y = point

                points = [
                    (x, y+1),
                    (x, y-1),
                    (x+1, y),
                    (x-1, y)
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

            # Try to place a room at the selected wall point.

            if make_fn(level, wall_point):
                reject_count = 0
            else:
                reject_count += 1

        # A downwards stairway should not be placed on the last level.
        if down_stairs:
            down_x, down_y = random.choice(get_tiles(level, FLOOR))
            level.tiles[down_x][down_y] = new_tile(DOWN_STAIRS)

        return level

    # The first level in the `World` object is generated without an
    # upwards stairway. The last level is generated without a
    # downwards stairway.

    world = ([make_level(False, True)]
        + [make_level(True, True) for _ in range(levels - 2)]
        + [make_level(True, False)])

    add_entity(world[0], (centre, centre), hero)
    return World(world, (centre, centre))

def new_tile(type_: TileType) -> Tile:
    """Returns a new, empty `Tile` object."""
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
    """Fills a rectangular area on `level`.

    point: the bottom left point of the rectangle to fill.
    """
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
    """Fills a rectangular area on `level`.

    The area is only filled if every tile in the area has a type of
    `SOLID_EARTH`. Returns true if successful, false otherwise.
    """
    validate(check_fill_rect, locals())

    x, y = point
    top_right = (x + width, y + height)
    level_length = len(level.tiles)

    # The bounds of the area need to be checked to ensure the whole
    # rectangle fits on the level.

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

    # Each direction is checked in turn to see if a room can be placed
    # there. If there is no space on any side, return `False`.

    # North
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

    # South
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

    # East
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

    # West
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

    return False

def make_corridor(level: Level, wall_point: tuple) -> bool:
    """Create a corridor on `level` at `wall_point`.

    The tile at `wall_point` should be a wall.
    """
    validate(make_corridor, locals())

    x, y = wall_point
    length = random.randint(5, 15)

    # Each direction is checked in turn to see if a corridor can be
    # placed there. If there is no space on any side, return `False`.

    # North
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

    # South
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

    # East
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

    # West
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
    level.entities[level.entities.index(point)] = None

def step(world: World):
    """Update `world` by one step.

    The contents of `world` may by modified.
    """
    validate(step, locals())

    level_length = len(world.current_level.tiles)

    # If new monsters can still be placed, try and place one on a
    # random floor tile.

    if len(world.current_level.entities) - 1 < MAX_MONSTERS:

        x = random.randrange(level_length)
        y = random.randrange(level_length)
        tile = world.current_level.tiles[x][y]

        if (tile.entity is None
                and tile.type is FLOOR
                and rand_chance(0.2)):

            # Only the monsters appropriate to the current level must
            # be chosen.

            monster_fn = random.choice(
                renethack.entity.monster_fns[len(world.upper_levels)])

            add_entity(world.current_level, (x, y), monster_fn())

    updated_entities = []

    # Each entity must only be updated once during each world update.

    for entity_point in world.current_level.entities:

        # Points containing deleted entities become `None` in the
        # entity list.

        if entity_point is None:
            continue

        x, y = entity_point
        entity = world.current_level.tiles[x][y].entity

        if entity in updated_entities:
            continue

        updated_entities.append(entity)
        old_world_len = len(world.upper_levels)
        entity.step(entity_point, world)

        hero_x, hero_y = world.hero
        hero = world.current_level.tiles[hero_x][hero_y].entity

        # If the current level has changed or the hero has died, the
        # function must return immediately.

        if old_world_len != len(world.upper_levels):
            return

        elif hero is None:
            return

    world.current_level.entities = [
        p for p in world.current_level.entities
        if p is not None
        ]

elements = [make_room, make_corridor]
# The list of functions that add an element to a level.
